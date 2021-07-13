import os

class TempFiles:
    """Clean up temporary files"""
    def __init__(self,
        base_filename):
        self.base_filename = base_filename
        self.temp_files=[]

    def compose_filename(self, suffix,is_temp=False):
        """Add suffix to BASE_FILENAME to compose new unique filename"""
        new_filename = self.base_filename + "." + suffix
        if is_temp:
            self.add_temp_file(new_filename)

        return new_filename

    def add_temp_file(self, filename):
        """Add temporary filename from output folder"""
        if filename not in self.temp_files:
            self.temp_files.append(filename)

    def delete_temp_files(self):
        """Delete all files marked as temp"""
        for file in self.temp_files:
            if os.path.isfile(file):
                os.remove(file)