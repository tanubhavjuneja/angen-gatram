import zipfile
import xml.etree.ElementTree as ET

file_path = "E:\log.xlsx"

def print_xml_metadata(zip_file, file_name):
    try:
        with zip_file.open(file_name) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            
            print(f"\n---- {file_name} ----")
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    print(f"{elem.tag} : {elem.text.strip()}")
    except KeyError:
        print(f"{file_name} not found.")

with zipfile.ZipFile(file_path, 'r') as z:
    print_xml_metadata(z, "docProps/core.xml")
    print_xml_metadata(z, "docProps/app.xml")
    print_xml_metadata(z, "docProps/custom.xml")