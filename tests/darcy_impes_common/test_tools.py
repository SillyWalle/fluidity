from batch_tools import Command, CommandList, verbose, HandlerLevel, \
    CompositeHandler, LeafHandler
import os
import re
import subprocess
import numpy
import sys
from fluidity_tools import stat_parser

error_rates_filename = "error_rates.txt"
error_norms_filename = "error_norms.txt"

## HELPER FUNCTIONS/CLASSES

def join_with_underscores(strings):
    result = None
    for s in strings:
        # for flexibility, any nil values are ignored
        if s is None: continue
        if result is None:
            result = s
        else:
            result = result + '_' + s
    return result


## FOR PUBLIC USE 
   
def find_in_open(report, key):
    """Searches a report and returns the value associated with key
    (ID). """
    report.seek(0)
    v = numpy.nan
    for l in report:
        if not l.strip(): continue
        if l.split()[0] == key: 
            v = float(l.split()[1])
            break
    return v

    
def find(report_filename, key):
    """Opens and searches report_filename and returns the value associated
    with key (ID).
    """
    with open(report_filename, "r") as f:
        v = find(f, key)
        return v

def find_norm(key): return find(error_norms_filename, key)
def find_rate(key): return find(error_rates_filename, key)

    
class WriteXMLSnippet(Command):
    def __init__(self, xml_file, metric_type, threshold, solution_dict):
        self.xml_file = xml_file
        self.metric_type = metric_type
        if metric_type=='norm':
            self.rel_op = 'lt'
        else:
            self.rel_op = 'gt'
        self.threshold = threshold
        self.solution_dict = solution_dict
        self.stem = None
        self.model = None
        self.dim = None
        self.mesh_type = None
        self.phase_index = None
        self.var_name = None
        self.field_short = None
        self.norm = None
        self.mesh_suffix_0 = None
        
      
    def execute(self, level_name, value, indent):
        if level_name == 'stem':
            self.stem = value
        if level_name == 'dim':
            self.dim = value
        if level_name == 'mesh_type':
            self.mesh_type = value
        elif level_name == 'field':
            # split up field name into useful bits
            pattern = 'Phase(.)::(.*)'
            self.phase_index = re.sub(pattern, '\\1', value)
            self.var_name = re.sub(pattern, '\\2', value)
            self.field_short = str.lower(self.var_name)+self.phase_index
            # read in field magnitudes for computing the norm properly
            if self.metric_type=='norm':
                self.rescaled_threshold = self.threshold*self.solution_dict[
                    self.field_short+'_scale']
            else:
                self.rescaled_threshold = self.threshold
            
        elif level_name == 'norm':
            self.norm = value
            # important to signal that this is the first mesh before
            # iterating over mesh suffices (resolutions)
            self.mesh_suffix_0 = None
            
        if level_name == 'mesh_suffix':
            mesh_suffix = value
        
            key_stem = join_with_underscores((
                self.model, str(self.dim)+'d', self.mesh_type,
                self.field_short, 'l'+str(self.norm)))
            
            if self.metric_type=='norm':
                key = join_with_underscores((key_stem, mesh_suffix))
            else:
                if self.mesh_suffix_0 is None:
                    self.mesh_suffix_0 = mesh_suffix
                    return
                key = join_with_underscores((key_stem,
                                             self.mesh_suffix_0+mesh_suffix))
                self.mesh_suffix_0 = mesh_suffix
    
            self.xml_file.write("""
    <test name="{1}: expect {0} {2} {3:g}" language="python">
from test_tools import find_rate
assert(find_{0}("{1}") &{2}; {3:g})
    </test>""".format(self.metric_type, key, self.rel_op, 
                      self.rescaled_threshold))


class RunSimulation(Command):

    def __init__(self):
        self.binary_path = "../../bin/darcy_impes"
        if not os.path.isfile(self.binary_path): 
            raise IOError("Cannot find the binary.")
        # can add more levels to this list
        self.stem = None
        self.model = None
        self.dim = None
        self.mesh_type = None

    def execute(self, level_name, value, indent):
        # can add more levels to this list
        if level_name == 'stem':
            self.stem = value
        elif level_name == 'model':
            self.model = value
        elif level_name == 'dim':
            self.dim = value
        elif level_name == 'mesh_type':
            self.mesh_type = value
        elif level_name == 'mesh_suffix':
            mesh_suffix = value

            filename = join_with_underscores((
                self.stem, self.model, str(self.dim)+'d',
                self.mesh_type, mesh_suffix)) + '.diml'
            
            # start simulation (TODO: guard against absent mesh)
            subprocess.call([self.binary_path, filename,
                             '-v3'], stdout=open(os.devnull, 'wb'))


class WriteToReport(Command):
    """Writes error norms and/or convergence rates to file"""

    def __init__(self, norms_file=None, rates_file=None):
        # both args are optional
        self.norms_file = norms_file
        self.rates_file = rates_file
        # can add more levels to this list
        self.stem = None
        self.model = None
        self.dim = None
        self.mesh_type = None
        self.phase_index = None
        self.var_name = None
        self.field_short = None
        self.norm = None
        self.mesh_suffix = None
        self.mesh_suffix_0 = None
        
    def execute(self, level_name, value, indent):
        if level_name!='mesh_suffix':
            level_str = '{0}{1}: {2}\n'.format(indent, level_name, value)
            if self.norms_file is not None:
                self.norms_file.write(level_str)
            if self.rates_file is not None:
                self.rates_file.write(level_str)
            
        # can add more levels to this list
        if level_name == 'stem':
            self.stem = value
        elif level_name == 'model':
            self.model = value
        elif level_name == 'dim':
            self.dim = value
        elif level_name == 'mesh_type':
            self.mesh_type = value
        elif level_name == 'field':
            # split up field name into useful bits
            pattern = 'Phase(.)::(.*)'
            self.phase_index = re.sub(pattern, '\\1', value)
            self.var_name = re.sub(pattern, '\\2', value)
            self.field_short = str.lower(self.var_name)+self.phase_index
        elif level_name == 'norm':
            self.norm = value
            # important to signal that this is the first mesh before
            # iterating over mesh suffices (resolutions)
            self.mesh_suffix_0 = None

        elif level_name == 'mesh_suffix':
            self.mesh_suffix = value

            err = self.get_norm()
            key_stem = join_with_underscores((
                self.model, str(self.dim)+'d', self.mesh_type,
                self.field_short, 'l'+str(self.norm)))

            if self.norms_file is not None:
                key = join_with_underscores((key_stem, self.mesh_suffix))
                self.norms_file.write('{0}{1}{2:12.3e}\n'.format(
                    indent, key, err))
                if verbose(): sys.stdout.write ('   err: {0:.3e}'.\
                                                format(err))

            # can only start computing rates from the 2nd mesh
            if self.rates_file is not None and self.mesh_suffix_0 is not None:
                # print a new ID and the rate
                key = join_with_underscores((key_stem, 
                                             self.mesh_suffix_0+self.mesh_suffix))
                rate = numpy.log2(self.err0/err)
                self.rates_file.write('{0}{1}{2:12.6f}\n'.format(
                    indent, key, rate))
                if verbose(): sys.stdout.write ('   rate: {0:.6f}'.\
                                                format(rate))
            self.err0 = err
            self.mesh_suffix_0 = self.mesh_suffix


    def get_norm(self):
        # Clients may want to override this method
        filename = join_with_underscores((
            self.stem, self.model, str(self.dim)+'d',
            self.mesh_type, self.mesh_suffix)) + '.stat'
        if self.norm==1:
            self.calc_type = "integral"
        elif self.norm==2:
            self.calc_type = "l2norm"
        return stat_parser(filename)\
            ['Phase'+self.phase_index]\
            [self.var_name+'AbsError']\
            [self.calc_type][-1]

               
# class Dummy(Command):
#    def __init__(self):
#       pass
#    def execute(self, level_name, value, indent):
#       pass
