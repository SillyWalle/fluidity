#!/usr/bin/env python

"""Extension of test_tools.py for MMS-based tests associated with the
Darcy IMPES code.

More documentation to come."""

import sys
sys.path.append('../../python')

import os
import string
import subprocess
import re
import numpy
from fluidity_tools import stat_parser
from solution_generator import generate
from importlib import import_module
from vtktools import vtu
from copy import deepcopy
from batch_tools import new_handler as nh
from batch_tools import Command
from test_tools import *

simulator_name = 'darcy_impes'
options_filename_extension = '.diml'


class ManufacturedSolutionParameteriser(DefaultParameteriser):
   def __init__(self, options_filename_extension,
                reference_mesh_res, reference_timestep_number):
      DefaultParameteriser.__init__(self, options_filename_extension)
      self.reference_mesh_res = reference_mesh_res
      self.reference_timestep_number = reference_timestep_number

   def element_number(self, domain_length):
      """Helper method.  Calculate element number along domain edge,
      keeping dx, dy and dz approximately the same but scaling
      consistently to higher mesh resolutions."""
      L0 = self.lookup('solution', 'domain_extents')[0]
      # reference number along edge in this dimension
      nref = numpy.round(self.reference_mesh_res*domain_length/L0)
      # number scaled up for this mesh resolution
      return int(nref * int(self.get('mesh_res')) \
                 / self.reference_mesh_res)
   
   def time_step(self):
      """Helper method.  Calculate an appropriate time step, maintaining
      a constant Courant number for all mesh resolutions."""
      finish_time = self.lookup('solution', 'finish_time')
      scale_factor = float(self.reference_mesh_res) \
          / float(self.get('mesh_res'))
      return scale_factor * finish_time / self.reference_timestep_number

   def geometry_dict(self):
      # initialise result
      result = { 'MESH_NAME': self.mesh_name() }
      # make entries for each dimension
      for i, dim_str in enumerate(('X', 'Y', 'Z')):
         L = self.lookup('solution', 'domain_extents')[i]
         n = self.element_number(L)
         result.update({
               'DOMAIN_LENGTH_{0}'.format(dim_str) : str(L),
               'EL_NUM_{0}'.format(dim_str) : str(n),
               'EL_SIZE_{0}'.format(dim_str) : str(L/n) })
      return result

   def options_dict(self):
      dim = self.get('dim')
      # some dictionary entries depend on whether 1D or multi-D
      if dim=="1":
         mesh_format = 'triangle'
         # these markers are for collapsing inappropriate wall BCs
         begin_rm_if_1D = '<!--'
         end_rm_if_1D = '-->'
      else:
         mesh_format = 'gmsh'
         begin_rm_if_1D = ''
         end_rm_if_1D = ''
      # other dictionary entries depend on whether 1D, 2D or 3D
      if dim=='1':
         outlet_ID = '2'
         inlet_ID = '1'
         wall_IDs = ''
         wall_num = '0'
      elif dim=='2':
         outlet_ID = '12'
         inlet_ID = '14'
         wall_IDs = '11 13'
         wall_num = '2'
      elif dim=='3':
         outlet_ID = '32'
         inlet_ID = '30'
         wall_IDs = '28 29 31 33'
         wall_num = '4'
      # now compile the dictionary 
      return {
         'MESH_NAME': self.mesh_name(),
         'MESH_FORMAT': mesh_format,
         'DOMAIN_DIM': dim,
         'TIME_STEP': str(self.time_step()),
         'FINISH_TIME': self.lookup('solution', 'finish_time'),
         'INLET_ID': inlet_ID,
         'OUTLET_ID': outlet_ID,
         'WALL_IDS': wall_IDs,
         'WALL_NUM': wall_num,
         'BEGIN_RM_IF_1D': begin_rm_if_1D,
         'END_RM_IF_1D': end_rm_if_1D }

   
class GenerateSymbols(TestCommand):
    def __init__(self, handler, parameteriser):
        TestCommand.__init__(self, ['case'], handler,
                            "Generating symbols", parameteriser)
        
    def execute(self):
        # the last level does everything.  Exit if we are not there yet
        if not self.at('leaf'):
            return
            
        # write dictionary
        solution_name = self.make_key()
        if self.verbosity > 0:
            div_plus_src = generate(solution_name, check_solution=True)
            sys.stdout.write('\n'+self.indent+
                             '   Sanity check; expect sum(div(u) - src) = 0...')
            for i in range(3):
                dim = i + 1
                sys.stdout.write(
                    '\n'+self.indent+'      {0}D: {1}'.\
                        format(dim, str(div_plus_src[i])))
        else:
            generate(solution_name)


class TestCommandDecorator(Command):
    def __init__(self, wrapped_test_command, solution_level_names):
        self.wrapped_test_command = wrapped_test_command
        self.solution_level_names = solution_level_names
        
    def inform(self, level_name, node_name, at_leaf, indent, verbose):
       """Delegation."""
       self.wrapped_test_command.inform(level_name, node_name,
                                        at_leaf, indent, verbose)

    def execute(self):
        """Imports generated expressions, if appropriate, before delegating
        to wrapped TestCommand"""
        # when this is the last of the solution levels, import generated
        # expressions
        if self.wrapped_test_command.get('level') == \
               self.solution_level_names[-1]:
           solution_name = self.wrapped_test_command.make_key(
              self.solution_level_names)
           self.solution_expressions = import_module(solution_name)
        
        # when this is the very last level, update the solution- and
        # level_dependent dictionaries
        if self.wrapped_test_command.at('leaf'):
           self.wrapped_test_command.update_dict(
              'solution', self.solution_expressions.py_dict)
           self.wrapped_test_command.update_dict(
              'options', self.solution_expressions.text_dict)
        
        # continue to wrapped execute()
        self.wrapped_test_command.execute()


    def handle(self, other=None, message=None):
        """Exploits the handler of the wrapped class."""
        self.wrapped_test_command.handle(self)

        
               
class ManufacturedSolutionTestSuite(TestSuite):
    """A front end for running various MMS-tailored
    TestCommands."""
   
    def __init__(self, case_name, mesh_type_list, mesh_res_lists,
                 field_list, norm_list, 
                 reference_mesh_res=5, reference_timestep_number=1,
                 command_line_in_xml=None,
                 norm_threshold=0.05, rate_threshold=0.8,
                 simulator_verbosity=0,
                 python_layer_verbosity=0, **kwargs):
        """In contrast to the inherited TestSuite, the present class builds its
        own handlers from lists supplied by the client.  The keyword
        args at the end can be used to make extra handlers at the
        solution level.  For example one might want to iterate over
        different values of pressure and saturation for a given test
        case.  Then one might specify: 'pressure', ['1000', '2000',
        '3000'], 'saturation', ['0.1', '0.2', '0.3'].

        """

        # make a handler for iteration over parameterised solutions
        self.solution_handler = nh('case', case_name)
        for level_name, node_names in kwargs.iteritems():
           solution_handler = solution_handler * nh(level_name, node_names)

        # extract a corresponding list of level names.  Continuing the
        # example given in the class description, one might end up with
        # ['case', 'pressure', 'saturation'].
        self.solution_level_names = self.solution_handler.get_level_names()

        # make another handler for meshing, simulations etc
        simulation_handler = deepcopy(self.solution_handler) * \
            nh('dim',
               [nh('1') * \
                    nh('mesh_res', mesh_res_lists[0]),
                nh('2') * \
                    nh('mesh_type', mesh_type_list) * \
                    nh('mesh_res', mesh_res_lists[1]),
                nh('3') * \
                    nh('mesh_type', mesh_type_list) * \
                    nh('mesh_res', mesh_res_lists[2])])
        
        # and a handler for configuring and computing norms and rates.
        # Note that mesh resolution always comes last.
        results_handler = deepcopy(self.solution_handler) * \
            nh('dim', [nh('1') * \
                           nh('field', field_list) * \
                           nh('norm', norm_list) * \
                           nh('mesh_res', mesh_res_lists[0]),
                       nh('2') * \
                           nh('mesh_type', mesh_type_list) * \
                           nh('field', field_list) * \
                           nh('norm', norm_list) * \
                           nh('mesh_res', mesh_res_lists[1]),
                       nh('3') * \
                           nh('mesh_type', mesh_type_list) * \
                           nh('field', field_list) * \
                           nh('norm', norm_list) * \
                           nh('mesh_res', mesh_res_lists[2])])

        # create an object for MMS-tailored parameterisations
        self.parameteriser = ManufacturedSolutionParameteriser(
           options_filename_extension, reference_mesh_res, 
           reference_timestep_number)

        # helper objects
        tc = DefaultThresholdCalculator(norm_threshold,
                                        rate_threshold)
                       
        # using the above objects, initialise the superclass
        TestSuite.__init__(
           self, simulation_handler, results_handler,
           parameteriser = self.parameteriser,
           command_line_in_xml = command_line_in_xml,
           threshold_calculator = tc,
           simulator_name = simulator_name,
           options_filename_extension = options_filename_extension,
           simulator_verbosity = simulator_verbosity,
           python_layer_verbosity = python_layer_verbosity)
        
    def create_generate_symbols_command(self):
       """New implementation."""
       return GenerateSymbols(self.solution_handler, self.parameteriser)

    def create_write_xml_file_command(self):
       """Method override.  Decorates the object created by the original
       TestSuite.
       """
       return TestCommandDecorator(
          TestSuite.create_write_xml_file_command(self),
          self.solution_level_names)

    def create_preprocess_command(self):
       """Method override.  Decorates the object created by the original
       TestSuite.
       """
       return TestCommandDecorator(
          TestSuite.create_preprocess_command(self),
          self.solution_level_names)