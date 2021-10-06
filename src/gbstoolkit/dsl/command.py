# TODO: I should really split this up into separate files for each category huh, this is becoming kinda a godclass
from abc import ABC, ABCMeta, abstractmethod
from typing import Dict, List, Optional, Union
from uuid import UUID

from kdl import Node

from .datatypes import ActorID, UnionArgument
from .enums import Direction, MoveType, RelativeActorPosition
from .marshalling import JsonSafe, serialize
from .util import NameUtil, NodeData, command_to_keyword

COMMANDS: Dict[str, "Command"] = {}  # Fills in automatically by subclassing Command! woooo

KEYWORDS: Dict[str, "Command"] = {}


# TODO: Better way to handle this in the future for compound data types! Type inference based on name?
def emergency_flatten(obj: JsonSafe) -> Union[int, float, str]:
    if type(obj) == int or type(obj) == float or type(obj) == str:
        return obj
    return str(obj)


# Should only ever autoregister Command instances, so if not then we've got a looot more problems on our hands
class AutoRegister(ABCMeta):
    def __init__(cls, name, bases, clsdict):
        if len(cls.mro()) == 4 and "name" in clsdict and "keyword" in clsdict:
            COMMANDS[cls.name()] = cls
            KEYWORDS[cls.keyword()] = cls
        super(AutoRegister, cls).__init__(name, bases, clsdict)

    @staticmethod
    def name() -> str:
        pass

    @staticmethod
    def keyword() -> str:
        pass


class Command(ABC, metaclass=AutoRegister):
    @staticmethod
    @abstractmethod
    def name() -> str:
        return NotImplemented

    @staticmethod
    @abstractmethod
    def keyword() -> str:
        return NotImplemented

    @staticmethod
    @abstractmethod
    def required_args() -> Optional[Dict[str, type]]:
        return None

    @staticmethod
    def children_names() -> Optional[List[str]]:
        return None

    @staticmethod
    @abstractmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NotImplemented

    @staticmethod
    @abstractmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return NotImplemented


class Fallback(Command):
    def __init__(self, name: str):
        self.fallback_name = name
        self.fallback_keyword = command_to_keyword(name)

    @staticmethod
    def name() -> str:
        return ""

    @staticmethod
    def keyword() -> str:
        return ""

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return None

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(
            {k: emergency_flatten(v) for k, v in args.items()} if args is not None else None,
            None
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {k: v for k, v in data.props.items() if k != "__eventid"}


class ActorCollisionsDisableCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_COLLISIONS_DISABLE"

    @staticmethod
    def keyword() -> str:
        return "disableCollision"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0])}


class ActorCollisionsEnableCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_COLLISIONS_ENABLE"

    @staticmethod
    def keyword() -> str:
        return "enableCollision"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0])}


class ActorEmoteCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_EMOTE"

    @staticmethod
    def keyword() -> str:
        return "emote"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "emoteId": str}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["emoteId"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "emoteId": data.args[1]}


class ActorGetDirectionCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_GET_DIRECTION"

    @staticmethod
    def keyword() -> str:
        return "storeDirection"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "direction": str}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["direction"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "direction": data.args[1]}


class ActorGetPositionCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_GET_POSITION"

    @staticmethod
    def keyword() -> str:
        return "storePosition"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "vectorX": str, "VectorY": str}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["vectorX"], args["vectorY"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {
            "actorId": names.id_for_actor(data.args[0]),
            "vectorX": data.args[1],
            "vectorY": data.args[2]
        }


class ActorHideCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_HIDE"

    @staticmethod
    def keyword() -> str:
        return "hide"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {
            "actorId": names.id_for_actor(data.args[0])
        }


class ActorInvokeCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_INVOKE"

    @staticmethod
    def keyword() -> str:
        return "interactWith"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {
            "actorId": names.id_for_actor(data.args[0])
        }


class ActorMoveRelativeCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_MOVE_RELATIVE"

    @staticmethod
    def keyword() -> str:
        return "moveBy"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        # x and y range -31 to 31
        return {"actorId": ActorID, "x": int, "y": int, "moveType": MoveType, "useCollisions": bool}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        if "verticalFirst" in args:
            args["moveType"] = "vertical" if args["verticalFirst"] else "horizontal"
        return NodeData(
            {"type": serialize(args["moveType"]), "collisions": args["useCollisions"]},
            [names.actor_for_id(args["actorId"]), args["x"], args["y"]]
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        if data.props is not None:
            type = MoveType.deserialize(data.props["type"])
            collisions = data.props["collisions"]
        else:
            type = MoveType.DIAGONAL
            collisions = False
        return {
            "actorId": names.id_for_actor(data.args[0]),
            "x": data.args[1],
            "y": data.args[2],
            "moveType": type.serialize(),
            "useCollisions": collisions
        }


class ActorMoveToCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_MOVE_TO"

    @staticmethod
    def keyword() -> str:
        return "moveTo"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        # x and y 0-255
        return {
            "actorId": ActorID,
            "x": UnionArgument[int],
            "y": UnionArgument[int],
            "moveType": MoveType,
            "useCollisions": bool
        }

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(
            {"type": serialize(args["moveType"]), "collisions": args["useCollisions"]},
            [
                names.actor_for_id(args["actorId"]),
                UnionArgument.format(args["x"], names),
                UnionArgument.format(args["y"], names)
            ]
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        if data.props is not None:
            type = MoveType.deserialize(data.props["type"])
            collisions = data.props["collisions"]
        else:
            type = MoveType.DIAGONAL
            collisions = False
        return {
            "actorId": names.id_for_actor(data.args[0]),
            "x": UnionArgument.parse(data.args[1], names),
            "y": UnionArgument.parse(data.args[2], names),
            "moveType": type.serialize(),
            "useCollisions": collisions
        }


class ActorPushCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_PUSH"

    @staticmethod
    def keyword() -> str:
        return "pushAway"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"continue": bool}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(args, None)

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return data.props


class ActorSetAnimateCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_ANIMATE"

    @staticmethod
    def keyword() -> str:
        return "setAnimate"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "animate": bool}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["animate"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "animate": data.args[1]}


class ActorSetAnimationSpeedCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_ANIMATION_SPEED"

    @staticmethod
    def keyword() -> str:
        return "setAnimSpeed"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "animSpeed": Union[None, int]}  # range null and 0-4

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["animSpeed"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "animSpeed": data.args[1]}


class ActorSetDirectionCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_DIRECTION"

    @staticmethod
    def keyword() -> str:
        return "setDirection"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "direction": UnionArgument[Direction]}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), UnionArgument.format(args["direction"], names)])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "direction": UnionArgument.parse(data.args[1], names)}


class ActorSetFrameCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_FRAME"

    @staticmethod
    def keyword() -> str:
        return "setFrame"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "frame": UnionArgument[int]}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), UnionArgument.format(args["frame"], names)])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "frame": UnionArgument.parse(data.args[1], names)}


class ActorSetMovementSpeedCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_MOVEMENT_SPEED"

    @staticmethod
    def keyword() -> str:
        return "setMoveSpeed"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "speed": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["speed"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "speed": data.args[1]}


class ActorSetPositionCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_POSITION"

    @staticmethod
    def keyword() -> str:
        return "setPosition"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "x": UnionArgument[int], "y": UnionArgument[int]}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(
            None,
            [
                names.actor_for_id(args["actorId"]),
                UnionArgument.format(args["x"], names),
                UnionArgument.format(args["y"], names)
            ]
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {
            "actorId": names.id_for_actor(data.args[0]),
            "x": UnionArgument.parse(data.args[1], names),
            "y": UnionArgument.parse(data.args[2], names)
        }


class ActorSetPositionRelativeCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_POSITION_RELATIVE"

    @staticmethod
    def keyword() -> str:
        return "changePosition"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "x": int, "y": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), args["x"], args["y"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "x": data.args[1], "y": data.args[2]}


class ActorSetSpriteCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SET_SPRITE"

    @staticmethod
    def keyword() -> str:
        return "setSprite"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "spriteSheetId": UUID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"]), names.sprite_for_id(args["spriteSheetId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0]), "spriteSheetId": names.id_for_sprite(data.args[1])}


class ActorShowCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_SHOW"

    @staticmethod
    def keyword() -> str:
        return "show"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0])}


class ActorStopUpdateScriptCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ACTOR_STOP_UPDATE"

    @staticmethod
    def keyword() -> str:
        return "stopUpdate"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [names.actor_for_id(args["actorId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"actorId": names.id_for_actor(data.args[0])}


class CallCustomEventCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_CALL_CUSTOM_EVENT"

    @staticmethod
    def keyword() -> str:
        return "call"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"customEventId": UUID}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        if len(args) > 2:
            props = {}
            for k, v in args.items():
                if "variable" in k:
                    props["var" + k[10:-2]] = "$" + v + "$"
                elif "actor" in k:
                    props["actor" + k[7:-2]] = names.actor_for_id(v)
        else:
            props = None
        return NodeData(props, [names.custom_event_for_id(args["customEventId"])])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        ret = {
            "customEventId": names.id_for_custom_event(data.args[0]),
            "__name": names.safe_custom_event_name(data.args[0])
        }
        if data.props is not None:
            for k, v in data.props:
                if k.startswith("var"):
                    ret["$variable[" + k[3:] + "]$"] = v[1:-1]
                elif k.startswith("actor"):
                    ret["$actor[" + k[5:] + "]$"] = names.id_for_actor(v)
        return ret


class CameraLockCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_CAMERA_LOCK"

    @staticmethod
    def keyword() -> str:
        return "lockCamera"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"speed": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [args["speed"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"speed": data.args[0]}


class CameraMoveToCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_CAMERA_MOVE_TO"

    @staticmethod
    def keyword() -> str:
        return "moveCameraTo"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"x": int, "y": int, "speed": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData({"speed": args["speed"]}, [args["x"], args["y"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"x": data.args[0], "y": data.args[1], "speed": data.props["speed"]}


class CameraShakeCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_CAMERA_SHAKE"

    @staticmethod
    def keyword() -> str:
        return "shakeCamera"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"shakeDirection": MoveType, "time": float}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [args["shakeDirection"], args["time"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        pass


class CommentCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_COMMENT"

    @staticmethod
    def keyword() -> str:
        return "note"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"text": str}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [args["text"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"text": data.args[0]}


class DataClearCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_DATA_CLEAR"

    @staticmethod
    def keyword() -> str:
        return "clearSave"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return None

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, None)

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return None


class DataLoadCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_DATA_LOAD"

    @staticmethod
    def keyword() -> str:
        return "loadSave"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return None

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, None)

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return None


class DataSaveCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_DATA_SAVE"

    @staticmethod
    def keyword() -> str:
        return "createSave"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return None

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, None)

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return None


# TODO: engine field stuff
class EngineFieldSetCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ENGINE_FIELD_SET"

    @staticmethod
    def keyword() -> str:
        return "setEngineField"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        pass

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        pass

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        pass


class EngineFieldStoreCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ENGINE_FIELD_STORE"

    @staticmethod
    def keyword() -> str:
        return "storeEngineField"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        pass

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        pass

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        pass


class FadeInCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_FADE_IN"

    @staticmethod
    def keyword() -> str:
        return "fadeIn"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"speed": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, [args["speed"]])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"speed": data.args[0]}


class FadeOutCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_ENGINE_FAD_OUT"

    @staticmethod
    def keyword() -> str:
        return "fadeOut"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"speed": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, args["speed"])

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return {"speed": data.args[0]}


# TODO: single child so make it a direct child (in event.py)
class GroupCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_GROUP"

    @staticmethod
    def keyword() -> str:
        return "group"

    @staticmethod
    def children_names() -> Optional[List[str]]:
        return ["true"]

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return None

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        return NodeData(None, None)

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        return None


class IfActorAtPositionCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_IF_ACTOR_AT_POSITION"

    @staticmethod
    def keyword() -> str:
        return "ifActorAtPosition"

    @staticmethod
    def children_names() -> Optional[List[str]]:
        return ["true", "false"]

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "x": int, "y": int}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        props = {}
        if "__disableElse" in args:
            props["__disableElse"] = args["__disableElse"]
        if "__collapseElse" in args:
            props["__collapseElse"] = args["__collapseElse"]
        return NodeData(
            props,
            [names.actor_for_id(args["actorId"]), args["x"], args["y"]]
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        ret = {"actorId": names.id_for_actor(data.args[0]), "x": data.args[1], "y": data.args[2]}
        if "__disableElse" in data.props:
            ret["__disableElse"] = data.props["__disableElse"]
        if "__collapseElse" in data.props:
            ret["__collapseElse"] = data.props["__collapseElse"]
        return ret


class IfActorFacing(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_IF_ACTOR_DIRECTION"

    @staticmethod
    def keyword() -> str:
        return "ifActorFacing"

    @staticmethod
    def children_names() -> Optional[List[str]]:
        return ["true", "false"]

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "direction": Direction}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        props = {}
        if "__disableElse" in args:
            props["__disableElse"] = args["__disableElse"]
        if "__collapseElse" in args:
            props["__collapseElse"] = args["__collapseElse"]
        return NodeData(
            props,
            [names.actor_for_id(args["actorId"]), args["direction"]]
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        ret = {"actorId": names.id_for_actor(data.args[0]), "direction": data.args[1]}
        if "__disableElse" in data.props:
            ret["__disableElse"] = data.props["__disableElse"]
        if "__collapseElse" in data.props:
            ret["__collapseElse"] = data.props["__collapseElse"]
        return ret


class IfActorRelativeTo(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_IF_ACTOR_RELATIVE_TO_ACTOR"

    @staticmethod
    def keyword() -> str:
        return "ifActorRelativeTo"

    @staticmethod
    def children_names() -> Optional[List[str]]:
        return ["true", "false"]

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"actorId": ActorID, "otherActorId": ActorID, "operation": RelativeActorPosition}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        props = {}
        if "__disableElse" in args:
            props["__disableElse"] = args["__disableElse"]
        if "__collapseElse" in args:
            props["__collapseElse"] = args["__collapseElse"]
        return NodeData(
            props,
            [
                names.actor_for_id(args["actorId"]),
                RelativeActorPosition.format(args["operation"]),
                names.actor_for_id(args["otherActorId"])
            ]
        )

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        ret = {
            "actorId": names.id_for_actor(data.args[0]),
            "operation": RelativeActorPosition.parse(data.args[1]),
            "otherActorId": names.id_for_actor(data.args[1])
        }
        if "__disableElse" in data.props:
            ret["__disableElse"] = data.props["__disableElse"]
        if "__collapseElse" in data.props:
            ret["__collapseElse"] = data.props["__collapseElse"]
        return ret


class TextDialogueCommand(Command):
    @staticmethod
    def name() -> str:
        return "EVENT_TEXT"

    @staticmethod
    def keyword() -> str:
        return "dialogue"

    @staticmethod
    def required_args() -> Optional[Dict[str, type]]:
        return {"text": Union[str, List[str]], "avatarId": Optional[UUID]}

    @staticmethod
    def format(args: Dict[str, JsonSafe], names: NameUtil) -> NodeData:
        text = args["text"]
        node_args = [names.sprite_for_id(args["avatarId"])] if "avatarId" in args and args["avatarId"] != "" else []
        if type(text) == str:
            children = None
            node_args.append(text)
        else:
            children = [Node("textbox", None, [i], None) for i in text]
        ret = NodeData(None, node_args, children)
        return ret

    @staticmethod
    def parse(data: NodeData, names: NameUtil) -> Optional[Dict[str, JsonSafe]]:
        if data.children is not None:
            text = [i.arguments[0].replace('\t', '') for i in data.children]
            avatar_id = data.args[0] if data.args is not None else None
        else:
            text = data.args[-1].replace('\t', '')
            avatar_id = data.args[0] if len(data.args) > 1 else None
        if avatar_id is not None:
            return {"avatarId": names.id_for_sprite(avatar_id), "text": text}
        else:
            return {"text": text}
