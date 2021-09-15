import json
import os


from dsl.project import Project
from dsl.util import sanitize_name


def make_actor_ref(project_file: str):
    if not os.path.exists("out"):
        os.mkdir("out")
    with open(project_file) as file:
        count_actors = 0
        count_scenes = 0
        contents = json.load(file)
        project = Project.deserialize(contents)
        for scene in project.scenes:
            count_scenes += 1
            scene_name = sanitize_name(scene.name, "Scene")
            seen_names = []
            actor_names = {}
            for actor in scene.actors:
                count_actors += 1
                name = actor.name
                if name == "":
                    name = "Actor " + str(scene.actors.index(actor))
                if name in seen_names:
                    name = name + " " + str(scene.actors.index(actor))
                    print("Found actor name " + actor.name + " in scene " + scene_name + " multiple times!")
                    print("Renaming to `" + name + "` for distinguishability.")
                    print("The original name will be preserved in the .gbsproj!")
                else:
                    seen_names.append(name)
                actor_names[actor.id] = (name, actor.name)
            path = "out/" + scene_name
            if not os.path.exists(path):
                os.mkdir(path)
            with open(path + "/actors.txt", mode="w") as outfile:
                outfile.write("".join([str(k) + ": " + v[0] + " (" + v[1] + ")\n" for k, v in actor_names.items()]))
        print("Found " + str(count_actors) + " actors in " + str(count_scenes) + " scenes!")





if __name__ == "__main__":
    make_actor_ref("samples/GBS Sample Project.gbsproj")
