#include <iostream>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <set>
#include <map>
#include <vector>




using namespace std;

//when cuda is added this file will be named main.cu as with the grid files
//This currently compiles and executes most of the preprocessing methods.

int main(){
    time_t start1 = time(nullptr);
    cout<<"\n\nPDB CLASSIFIER INITIATING>>>>>\n\n"<<endl;
    string c = "AMP ADP ATP CDP CTP GMP GDP GTP TMP TTP UMP UDP UTP";
    string d = "DA DC DG DT DI";
    string r = "A C G U I";
    string pp = "ALA CYS ASP GLU PHE GLY HIS ILE LYS LEU MET ASN PRO GLN ARG SER THR VAL TRP TYR";
    string w = "HOH";


    //this is where loop starts
    //need to specify
        //what types of proteins they are looking for
            //this will tell the loop when to exit for that protein
        //where the files are
        //ask if they would like the files to go anywhere but in folders at the destination
    bool hasDNA = false;
    bool hasRNA = false;
    bool hasLigand = false;
    bool hasCarbohydrate = false;
    bool hasCofactors = false;
    bool hasIons = false;
    string pathToFile = "5gsu.pdb";//this needs to be able to be changed
    string id = pathToFile.substr(pathToFile.length() - 8, 4);
    ifstream pdbstream(pathToFile);
    string currentLine;
    char checkChar = '-';
    string resName, atomName;
    if (pdbstream.is_open()) {
        while (getline(pdbstream, currentLine)) {
            if (currentLine.substr(0, 4) == "ATOM" || currentLine.substr(0, 6) == "HETATM") {
                resName = currentLine.substr(17, 4);
                atomName = currentLine.substr(12, 4);
                if (c.find(resName) != -1) {
                    hasCofactors = true;
                }
                else if (d.find(resName) != -1) {
                    hasDNA = true;
                }
                else if (r.find(resName) != -1) {
                    hasRNA = true;
                }
                else if (resName == atomName) {
                    hasIons = true;
                }
                else {
                    hasLigand = true;
                }
            }

        }
        pdbstream.close();
        cout <<"~"<<pathToFile<<" has been classified~" << endl;
    }
    else cout << "Unable to open: " + pathToFile << endl;
    return 0;
}
