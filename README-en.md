# input-tool
Tool which simplifies creating and testing inputs for programming contests. The tool consists of three parts -- input-sample, input-generator and input-tester.

# Installation and usage
You can install this tool on **Linux** by following this few steps.

1. Clone this repository. `git clone git@github.com:jablkoj/input-tool.git`.
   The tool is still under development. If you want to download a new version, just write `git pull` inside the   directory of repository.
2. Run `./install.sh`. It will create symlinks to programs inside `/usr/local/bin`. If will ask for root privilegies to create the symlink.


# input-sample
Not implemented yet

# input-generator

Recommended usage is like this. Implement **generator** and call it `gen` (e.g. `gen.cpp`, `gen.py`). Generator is program which gets one line on stdin (there can be anything you want on the line, e.g. three integers) and prints one input on stdout. 

Create input description file (short IDF). **One line of the IDF** is (almost) exactly what your **generator gets on stdin**. **Separate batches by empty line**. Don't use IDF for sample inputs. (Use input-sample script).

"Almost" means that there are special ways to make cool things, if you know how. Cool features are not documented yet. 

```
input-generator idf
input-generator -i . -I input -g gen.cpp -qK < idf
# You can use help to understand the previous line.
input-generator -h 
```
# input-tester
