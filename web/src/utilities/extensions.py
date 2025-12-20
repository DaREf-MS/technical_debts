from src.models.model import File

class Extensions: 
    def get_extension_set(file_list : list[File]) -> set[str]:
        file_extensions = set()
        for f in file_list: 
            #print(f.name)
            filename = str(f.name)
            tokens = filename.split(".")
            token_nb = len(tokens)
            if token_nb == 1:
                continue
            
            extension = "." + tokens[token_nb - 1]
            #print(extension)
            file_extensions.add(extension)
            continue
        return file_extensions
