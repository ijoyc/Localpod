import sublime
import sublime_plugin
import os
from os import path

PLUGIN_NAME = "Localpod"

class Pod(object):
    def __init__(self, name, start, end):
        self.name = name
        self.textRange = (start, end)

class runlocalpodCommand(sublime_plugin.WindowCommand):

    pod_list = []

    first_list = []
    second_list =[]
    chosen_pods = []
    replacement_map = {}

    # ====== Phase 1: Build Pod List ======

    def initialize(self):
        self.build_pod_list()
        self.chosen_pods = []
        self.replacement_map = {}
        self.first_list = list(map(lambda pod: pod.name, self.pod_list))
        self.second_list = ['Done'] + self.first_list

    def build_pod_list(self):
        view = self.window.active_view()
        all_content_range = sublime.Region(0, view.size())
        all_content = view.substr(all_content_range)

        regexp = 'pod\\s*[\'\"]([_a-zA-Z][_a-zA-Z0-9]*)[\'\"]\\s*,\\s*([\'\"][^\'\"]+[\'\"])'
        extraction = []
        result = view.find_all(regexp, sublime.IGNORECASE, "$1", extraction)
        self.pod_list = list(map(lambda group: Pod(group[1], group[0].a, group[0].b), zip(result, extraction)))

    # ====== Phase 2: Find Local Pods ======

    def find_local_pods(self):
        unfound_pods = []
        for pod in self.chosen_pods:
            pod_path = self.configured_path_for_pod_name(pod)
            if pod_path is None:
                unfound_pods.append(pod)
            else:
                self.replacement_map[pod] = pod_path
        if len(unfound_pods) > 0:
            self.search_paths_for_pod_names(unfound_pods)

    def configured_path_for_pod_name(self, name):
        abs_paths = load_settings().get('abs_paths_for_pods')
        if not name in abs_paths:
            return None
        pod_path = path.expanduser(abs_paths[name])

        view = self.window.active_view()
        file_dir = path.dirname(view.file_name())

        return path.relpath(pod_path, file_dir)

    def search_paths_for_pod_names(self, names):
        view = self.window.active_view()
        file_dir = path.dirname(view.file_name())
        work_directory = path.expanduser(load_settings().get('work_directory'))
        abs_paths = load_settings().get('abs_paths_for_pods')

        for root, dirs, files in os.walk(work_directory):
            if len(names) == 0:
                break
            for file in files:
                filename, fileext = path.splitext(file)
                if (not path.isdir(file)) and fileext == '.podspec' and filename in names:
                    result_path = path.relpath(root, file_dir)
                    self.replacement_map[filename] = result_path

                    abs_paths[filename] = root
                    names.remove(filename)

        load_settings().set('abs_paths_for_pods', abs_paths)
        save_settings()

    # ====== User Interaction ======

    def show_quick_panel(self, options, done):
        sublime.set_timeout(lambda: self.window.show_quick_panel(options, done), 10)

    def first_select(self, index):
        if index > -1:
            self.chosen_pods.append(self.first_list[index])
            self.second_list.remove(self.first_list[index])
            self.show_quick_panel(self.second_list, self.second_select)

    def second_select(self, index):
        if index == 0:
            self.on_select_finish()
        elif index > 0:
            self.chosen_pods.append(self.second_list[index])
            self.second_list.remove(self.second_list[index])
            self.show_quick_panel(self.second_list, self.second_select)

    def on_select_finish(self):
        self.find_local_pods()
        view = self.window.active_view()
        pod_list = {}
        for pod in self.pod_list:
            pod_list[pod.name] = pod.textRange
        view.run_command('writelocalpod', {'pod_list': pod_list, 'replacement_map': self.replacement_map})

    def run(self):
        self.initialize()
        self.show_quick_panel(self.first_list, self.first_select)


class writelocalpodCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        all_pod_list = kwargs['pod_list']
        replacement_map = kwargs['replacement_map']
        filtered_pod_list = dict(filter(lambda pair: pair[0] in replacement_map.keys(), all_pod_list.items()))
        filtered_pods = list(map(lambda x: Pod(x[0], x[1][0], x[1][1]), filtered_pod_list.items()))
        sorted_pods = list(sorted(filtered_pods, key=lambda pod: pod.textRange[0], reverse=True))

        for pod in sorted_pods:
            name = pod.name
            path = replacement_map[name]
            textRange = sublime.Region(pod.textRange[0], pod.textRange[1])
            self.view.replace(edit, textRange, "pod '%s', :path => '%s'" % (name, path))



# ====== Utils ======

def load_settings():
    return sublime.load_settings('%s.sublime-settings' % PLUGIN_NAME)

def save_settings():
    sublime.save_settings('%s.sublime-settings' % PLUGIN_NAME)






