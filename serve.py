from flask import Flask, abort, render_template, send_file, send_from_directory
import sys
import os
#####################
# sys.path.append(os.path.abspath("../isbn_images") )
from tiles import ImageTileGen, generateLevels, recursive_tile_index
from scales import smaller_sizes,base_size
#####################
app = Flask(__name__)

IMAGE_DIRECTORY = "images"


images = [
["All ISBNs" ,"all"],
["Files in Anna’s Archive" ,"md5"],
["CADAL SSNOs" ,"cadal_ssno"],
["CERLALC data leak" ,"cerlalc"],
["DuXiu SSIDs" ,"duxiu_ssid"],
["EBSCOhost’s eBook Index" ,"edsebk"],
["Google Books" ,"gbooks"],
["Goodreads" ,"goodreads"],
["Internet Archive" ,"ia"],
["ISBNdb ","isbndb"],
["ISBN Global Register of Publishers" ,"isbngrp"],
["Libby" ,"libby"],
["Nexus/STC" ,"nexusstc"],
["OCLC/Worldcat" ,"oclc"],
["OpenLibrary" ,"ol"],
["Russian State Library" ,"rgb"],
["Imperial Library of Trantor ","trantor"],
]
   

 
@app.route('/')
def list_images():

    return render_template('isbn.html', images=images)



@app.route('/tile/<group>/<int:level>/<tile>.png')
def serve_tile(group,level,tile):
    for j in images:
       if(j[1] == group):
        group = f"_{group}_isbns"

        trtile = recursive_tile_index(tile)

        print(trtile,tile)


        tile = trtile
        tile_size = base_size
        if(level> 4): level = 4


        levelsize = smaller_sizes[level]
        levelwidth = levelsize[0]
        levelheight = levelsize[1]
        groupdir = None

        if (level == 4):
            groupdir = os.path.join(IMAGE_DIRECTORY, group)
        else:
            groupdir = os.path.join(os.path.join(IMAGE_DIRECTORY, group), f"{levelwidth}x{levelheight}")


        path  = os.path.join(groupdir, f"tile_{tile}.png")
        if (os.path.exists(path)):
            return send_file(path)

        gen = generateLevels(os.path.join(IMAGE_DIRECTORY, group) ,tile_size, smaller_sizes, 4,0,0)


        if(gen == None):
            return abort(404)
        else:
            return  send_file(gen.path)

    
if __name__ == '__main__':
    app.run(debug=True) 
    
 
    
 
