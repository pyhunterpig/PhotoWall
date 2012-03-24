'''
Created on Mar 23, 2012

@author: lloydsheng
'''
import os
import random
import shutil

class Lettory():
    def __init__(self,  base_dir):
        random.seed()
        self.base_dir = base_dir
        self.avatar_path = os.path.join(base_dir, "avatar")
        self.result_path = os.path.join(base_dir, "result")
        self.avatar_names = [file for file in os.listdir(self.avatar_path) if not os.path.isdir(os.path.join(self.avatar_path, file))]
        self.current_index = 0
        
    def next_people_avatar(self):
        if self.avatar_names:
            self.current_name = random.choice(self.avatar_names)
            return os.path.join(self.avatar_path, self.current_name)
    
    def save_lucky_people(self):
        self.current_index += 1
        src = os.path.join(self.avatar_path, self.current_name)
        dst = os.path.join(self.result_path, "%s.jpg" % self.current_index)
        shutil.copy(src, dst)
        self.avatar_names.remove(self.current_name)
        