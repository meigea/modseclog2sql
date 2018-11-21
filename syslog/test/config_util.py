import configparser  # 导入 configparser包

class client_info(object):
    def __init__(self, file):
        self.file = file
        self.cfg = configparser.ConfigParser()  # 创建一个 管理对象。

    def cfg_load(self):
        self.cfg.read(self.file)  # 把 文件导入管理对象中，把文件内容load到内存中

    def cfg_dump(self):
        se_list = self.cfg.sections()  # cfg.sections()显示文件中的所有 section
        print('<======CONFIG=====>')
        for se in se_list:
            print("\t\t<= " + se + " =>")
            print(dict(self.cfg.items(se)))
        print('</=====END-CONFIG=====>')

    """单个section通过json格式导入"""
    def add_section_items(self, section, temp_dict):
        if not self.cfg.has_section(section):
            self.add_section(section)
        for key in temp_dict.keys():
            self.set_item(section, key, temp_dict[key])

    """json格式导入"""
    def dump_by_json_config(self, res_json):
        for section in res_json.keys():
            self.add_section_items(section, res_json[section])

    def delete_item(self, se, key):
        self.cfg.remove_option(se, key)  # 在 section 中删除一个 item

    def delete_section(self, se):
        self.cfg.remove_section(se)  # 删除一个 section

    def add_section(self, se):
        self.cfg.add_section(se)  # 添加一个 section

    def set_item(self, se, key, value):
        self.cfg.set(se, key, value)

    def save(self):
        fd = open(self.file, 'w')
        self.cfg.write(fd)
        fd.close()

def demo_test():
    ## print(s.encode('gbk').decode('utf-8'))
    info = client_info('settings.ini')
    info.cfg_load()
    info.dump_by_json_config({
        "manager": {
            "name": 'actanble',
            "email": "actanble@gmail.com",
            "personal_net": 'http://www.kac.fun',
        },
        "deppend_url": {
            "url": 'blog.csdn.net/actanble',
            "desc": 'No_add_desc',
        },
    })
    info.cfg_dump()
    info.save()
