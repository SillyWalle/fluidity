input: clean
	gmsh -2 -bin src/squareA.geo -o squareA.msh
	gmsh -2 -bin src/squareB.geo -o squareB.msh

clean:
	rm -rf *.msh *.stat *.vtu *.log-0 *.err-0 *checkpoint *.convergence *.log *.node *.edge *.ele *.halo *.pvtu viscous_fs_zhong_B_* viscous_fs_zhong_A_* fluidity.* *.pyc
