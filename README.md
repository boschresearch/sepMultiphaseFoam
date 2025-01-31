# Fast Evaporation Simulation in Gaps (FESIG)  <!-- omit in toc -->

This branch contains the implementations and test cases studied in the paper "A Novel Simulation Approach for Evaporation Processes in Small Gaps of Industrial Applications" (Publication on [Elsevier](), Preprint on [ArXiV](https://arxiv.org/pdf/2501.09337)).

<span style="color:red">**under construction**</span>
Code will be published soon.

## Table of Contents  <!-- omit in toc -->

- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
- [Usage](#usage)
  - [Preparation](#preparation)
  - [Execution](#execution)
- [Additional information](#additional-information)
  - [Placeholders and dictionary](#placeholders-and-dictionary)
- [About](#about)
  - [Maintainers](#maintainers)
  - [Contributors](#contributors)
- [License](#license)

## Getting Started <a name="getting-started"></a>

### Requirements <a name="requirements"></a>
- Python package trimesh must be installed in conda environment (requires python>=3.7)
- The program is tested with miniconda==4.11 and python==3.10

### Installation <a name="installation"></a>

1. Install Surface Evolver
	- Download the Surface Evolver version 2.70 from [here](https://kenbrakke.com/evolver/downloads/evolver-2.70.tar.gz)
	- Transfer the downloaded archive to your home directory
	- Extract the archive in the home folder using <code>tar -xzf evolver-2.70.tar.gz .</code>
	- Now, a new directory named <code>evolver-2.70</code> should be located in your home directory
	- Follow the installation guide according to the [SE website](https://kenbrakke.com/evolver/html/install.htm#unix-version) to complete the installation. Especially, take care of the respective changes in the Surface Evolver Makefile to avoid errors during program execution.
2. Install OpenFOAM v2212 from the ESI [website](https://www.openfoam.com/news/main-news/openfoam-v2212)
3. Install Surface Evolver convergence algorithm and customized OpenFOAM solver 
	- Open a new Linux terminal: <code>Ctrl+Alt+T</code>
	- Clone the git repository to your home directory: <code>git clone https://github.com/boschresearch/sepMultiphaseFoam.git</code>
	- Change to the newly created repository directory: <code>cd sepMultiphaseFoam</code>
	- Check out the correct branch <code>git checkout publications/novelSimulationApproachForEvaporationProcesses</code>
	- Execute installation script: <code>./setup.sh</code>. The installation script automatically executes the following steps:
		1. Install convergence algorithm according to the algorithm used by SE-FIT ([SE-FIT website](https://www.se-fit.com/))
		2. Set up calculation routine for convergence algorithm
		3. Install custom OpenFOAM solver for steady-state Laplace equation
		4. Add aliases in .bashrc

## Usage <a name="usage"></a>

### Preparation <a name="preparation"></a>

Best Practice is to use a tutorial that fits your personal case best and just change parameters in the parameter dictionary. In version 1.0.0, the automatic creation of the capillary geometry including the environment (called <code>enclosure.stl</code>), is not implemented yet. As a consequence geometry variations must be treated in multiple cases.
As a solution, you can create the <code>enclosure.stl</code> yourself using OpenFOAM. OpenFOAM templates are available for round capillaries, square capillaries and gaps and can be found under <code>src/create_enclosure_stl</code>. To create the <code>enclosure.stl</code> file, follow these steps:
1. Navigate to the respective directory (round/square/gap) in the console
2. Source OpenFOAM using the <code>of2212</code> command
3. Replace the placeholders in the <code>system/blockMeshDict_tmplt</code> file with the respective values from your parameter dictionary <code>&lt;caseName&gt;.pd</code> and save <code>system/blockMeshDict_tmplt</code> as <code>blockMeshDict</code>.
4. Start the STL creation with <code>./createGeomAndExportSTL</code>
5. Copy the newly created <code>enclosure.stl</code> file to <code>&lt;caseName&gt;/INPUT/&lt;caseName&gt;_OF/constant/triSurface</code>.

It is not recommended, but if you want to start a new case from scratch, follow these guidelines:

1. Create a top level folder <code>&lt;caseName&gt;</code>.
2. Create a new folder <code>INPUT</code> inside the <code>&lt;caseName&gt;</code> folder. All input data is stored here.
3. For the program to work, the following directories/files must be given by the user in the <code>INPUT</code> directory:
  - <code>&lt;caseName&gt;.fes</code> (file): Surface Evolver file. Defines the capillary geometry and incorporates variable placeholders. For more information on <code>fes</code>-file setup, have a look at the Surface Evolver manual [here](https://kenbrakke.com/evolver/downloads/manual270.pdf).
  - <code>&lt;caseName&gt;.pd</code> (file): Parameter dictionary. Contains variable placeholder names and values for the variable placeholders in the <code>fes</code>-file and the OpenFOAM directory. A more detailed description about the dictionary and placeholders can be found [here]().
  - <code>&lt;caseName&gt;_OF</code> (directory): OpenFOAM template directory. Contains the OpenFOAM simulation case structure.

### Execution <a name="execution"></a>

Open a new console and navigate to the top level folder named <code>&lt;caseName&gt;</code>. Type <code>fesig</code> in the console and hit Enter.

## Additional information <a name="additional-information"></a>

### Placeholders and dictionary <a name="placeholders-and-dictionary"></a>
- Placeholders are always characterized by the opening characters <code>|-</code>, followed by a placeholder name <code>PLACEHOLDER_NAME</code> and the closing characters <code>-|</code> (e.g. <code>|-SIGMA-|</code>). By convention, the placeholder name is capitalized and words are separated by underline <code>\_</code>. 
- In the placeholder dictionary all placeholders must be specified except for some internal variables for number of CPUs, memory per CPU, ...
	- The dictionary must be legible by Python and has to start with <code>{</code> and end with <code>}</code>
	- The dictionary keys are placeholder names
	- The dictionary values are a nested dictionary consisting of the values list <code>vals</code> to be inserted in the placeholders and a program flag <code>prog_flag</code> which specifies if the placeholder is used in Surface Evolver <code>se</code> or OpenFOAM <code>of</code>.
	- Example:
	<pre><code>
	{
		'PLACEHOLDER_NAME': {'vals': [1,2,3,4,5], 'prog_flag': 'se'}
	}</code></pre>

## About <a name="about"></a>

### Maintainers <a name="maintainers"></a>

Phil Namesnik<br>
Anja Lippert<br>
Tobias Tolle<br>
Christian Kuntz<br>
Alexander Eifert

### Contributors <a name="contributors"></a>

Phil Namesnik<br>
Louis Mett<br>
Anja Lippert<br>
Tobias Tolle<br>
Christian Kuntz<br>
Alexander Eifert

## License <a name="license"></a>

FESIG is open-sourced under the AGPL-3.0 license. See the [LICENSE](LICENSE) file for details.

For a list of other open source components included in FESIG, see the file [3rd-party-licenses.txt](3rd-party-licenses.txt).