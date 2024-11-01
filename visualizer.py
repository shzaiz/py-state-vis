import inspect
import re
import pydot
import sys
import copy

class Visualizer:
    # On encountering PRIMITIVE_TYPES, just show String repr
    PRIMITIVE_TYPES = (int, float, str, bool, type(None))
    # Do not expand PRIMITIVE_CLASSES
    PRIMITIVE_CLASSES = {tuple, type, dict}
    def __init__(self):

        # Keep record of which elements has been visited to avoid loop
        self.visited = {}

    def is_class(self, dat):
        """Check whether data a class type"""
        return isinstance(dat, type)

    def is_instance(self, dat):
        """Check whether dat is an instance"""
        return type(dat) not in self.PRIMITIVE_TYPES and \
               isinstance(type(dat), type) and \
               not isinstance(dat, type)

    def get_name(self, obj):
        """Get type(class) name of the object"""
        return obj.__name__ if hasattr(obj, '__name__') else self.get_name(type(obj))

    def encode_primitive(self, obj) -> str:
        """Encode primitive objects, by their string representations"""
        return str(obj)

    def get_variable_name(self, var):
        """Get the variable name of an object"""
        # The current object has at least 2 calls(visualize -> get_variable_name)
        # Hence we get the stack in reverse to avoid newer names shadowed by older
        # ones
        symbtab = inspect.stack()[2:][::-1]

        for oldframe in symbtab:
            for name, value in oldframe.frame.f_locals.items():
                if value is var:
                    return name

        # If we did not found the name, find in global var names
        for name, value in globals().items():
            if value is var:
                return name

    def normalize(self, original_string):
        """Make sure the string of label will not crash DOT engine"""
        modified_string = re.sub(r'(?<!\\)<', r'\<', original_string)
        modified_string = re.sub(r'(?<!\\)>', r'\>', modified_string)
        modified_string = re.sub(r'(?<!\\){', r'\{', modified_string)
        modified_string = re.sub(r'(?<!\\)}', r'}', modified_string)
        modified_string = re.sub(r'(?<!\\)\[', r'\[', modified_string)
        modified_string = re.sub(r'(?<!\\)\]', r'\]', modified_string)
        modified_string = re.sub(r'\n', r'  ', modified_string)
        return modified_string

    def visualize(self, obj):
        """Entry of object visualization."""
        if type(obj) in self.PRIMITIVE_TYPES:
            # Do not try to recursively expand primitive types
            return self.visualize_primitive(obj)
        elif type(obj) == 'module':
            # Do not dig into modules
            return self.visualize_primitive(obj.__name__)
        elif isinstance(obj, dict):
            return self.visualize_dict(obj)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            return self.visualize_list(obj)
        elif isinstance(obj, object):
            # We are not expecting to visualize system components, 
            # i.e. signals, files, wrappers and so on. 
            # no other classes except __main__
            if obj.__class__.__module__ not in ('__main__'):
                return None
            return self.visualize_instance(obj)

    def visualize_primitive(self, obj):
        # varname being the unique identifier of the current component
        varname = id(obj) 
        graph = pydot.Subgraph(graph_type='digraph', subgraph_name=varname)
        record_node = pydot.Node(varname, shape='record')

        # create [name | content] (In fact this is not variable, rather, ref)
        fields = self.get_variable_name(obj) + "|" + str(obj)
        record_node.set_label(fields)
        graph.add_node(record_node)
        return graph

    def visualize_list(self, lst: list):
        varname = id(lst)
        graph = pydot.Subgraph(graph_type='digraph', subgraph_name=id(lst))

        record_node = pydot.Node(varname, shape='record')
        
        # recursively draw the contents of the list, at the same time avoid visiting the 
        # same ones
        if varname in self.visited:
            graph.add_node(record_node)
            return graph
        self.visited[varname] = True

        # Add records to this
        fields = '|'.join([f'<{i}> {self.normalize(str(value))}' for i, value in enumerate(lst)])
        record_node.set_label(f'{{ {self.get_variable_name(lst)} | {fields} }}')
        graph.add_node(record_node)

        # point list childrens to proper places
        for i, item in enumerate(lst):
            if type(item) in self.PRIMITIVE_TYPES:
                # We do not point it to primitive_types to keep the graph clean
                continue
            else:
                subgraph = self.visualize(item)
                if subgraph is not None:
                    graph.add_subgraph(subgraph)
                    graph.add_edge(
                        pydot.Edge(
                            src=f"{record_node.get_name()}:<{i}>", 
                            dst=subgraph.get_node_list()[0]
                            )
                        )

        return graph
    
    def visualize_dict(self, obj):
        varname = id(obj)
        graph = pydot.Subgraph(graph_type='digraph', subgraph_name=varname)
        record_node = pydot.Node(varname, shape='record')
        if varname in self.visited:
            graph.add_node(record_node)
            return graph
        self.visited[varname] = True

        fields = '|'.join([f'<{i}> {self.normalize(str(i))}:{self.normalize(str(value))}' for i, value in obj.items()])
        record_node.set_label(f'{{ {self.get_variable_name(obj)} | {fields} }}')
        graph.add_node(record_node)

        for key, value in obj.items():
            if type(value) in self.PRIMITIVE_TYPES:
                continue
            else:
                subgraph = self.visualize(obj[key])
                if subgraph is not None:
                    graph.add_subgraph(subgraph)
                    graph.add_edge(
                        pydot.Edge(
                            src=f"{record_node.get_name()}:<{key}>", 
                            dst=subgraph.get_node_list()[0]
                            )
                        )
        return graph

    def visualize_instance(self, obj):
        self.visited[id(obj)] = True
        graph = pydot.Subgraph(graph_type='digraph', subgraph_name=id(obj))
        class_name = obj.__class__.__name__

        record_node = pydot.Node(id(obj), shape='record')
        names = [attr for attr in dir(obj)
                 if not attr.startswith('__') and not callable(getattr(obj, attr))]
        fields = [f"<{attr}> {attr} : {self.normalize(str(getattr(obj, attr)))}" for attr in names]

        label = f'{{ {class_name} | ' + '{' + ' | '.join(fields) + ' }}'
        record_node.set_label(label)

        for field in names:
            if type(getattr(obj, field)) in self.PRIMITIVE_TYPES:
                continue
            else:
                subgraph = self.visualize(getattr(obj, field))
                if subgraph is not None:
                    graph.add_subgraph(subgraph)
                    graph.add_edge(
                        pydot.Edge(
                            src=f"{record_node.get_name()}:<{field}>", 
                            dst=subgraph.get_node_list()[0]
                            )
                        )

        graph.add_node(record_node)
        return graph
    
    # TODO: These are iterable objects. Refactor them to get cleaner code
    
    def visualize_frame(self, frame):
        subgraph = pydot.Subgraph()
        for localvar in frame.f_locals:
            if isinstance(localvar, __class__):
                if localvar.__module__ not in ('__main__'):
                    continue
            if id(localvar) in self.visited or localvar.startswith('_') :
                continue
            sub = self.visualize(frame.f_locals[localvar])
            if sub is not None:
                subgraph.add_subgraph(sub)
        
        return subgraph
    
    def _find_elem_in_subgraph(self, subgraph:pydot.Subgraph):
        # TODO: This is OK to remove, since I have dummy code in childrens
        result = subgraph.get_node_list()
        if len(result) > 0:
            return result[0]
        
        cont_search = subgraph.get_subgraph_list()
        # print("Continue: ", cont_search)
        for i, _ in enumerate(cont_search):
            return self._find_elem_in_subgraph(cont_search[i])
        
        return None
    
    def visualize_whole_state(self, valid_frames_frm = 1, strict = False):
        graph = pydot.Dot(graph_type='digraph', strict=strict, compound=True, rankdir='TB')
        

        to_iter = inspect.stack()[valid_frames_frm:]
        subgraph = pydot.Subgraph()
        subgraph.set_rankdir('TB')
        previous_cluster= None
        # print(len(to_iter))
        for i, _ in enumerate(to_iter):
            subgraphi = self.visualize_frame(to_iter[i].frame)
            sentinal_node = pydot.Node("cluster_"+str(id(to_iter[i].frame)))
            sentinal_node.add_style("invisible")
            subgraphi.add_node(sentinal_node)
            subgraphi.set_name("cluster_"+str(id(to_iter[i].frame)))
            subgraphi.set_label(self.normalize(to_iter[i].function+":"+str(to_iter[i].frame.f_lineno)))
            subgraph.add_subgraph(subgraphi)
            if previous_cluster is not None:
                curr = self._find_elem_in_subgraph(subgraphi)
                prev = self._find_elem_in_subgraph(previous_cluster)
                if curr and prev:
                    # print("cluster_"+str(id(to_iter[i].frame)))
                    # print(curr.get_name(), prev.get_name())
                    subgraph.add_edge(pydot.Edge(
                        prev, 
                        curr, 
                        ltail = previous_cluster.get_name(), 
                        lhead=subgraphi.get_name(),
                    ))
            previous_cluster = subgraphi
            
        graph.add_subgraph(subgraph)
        return graph









