import {
  MdCheckBox,
  MdCheckBoxOutlineBlank,
  MdRemoveCircleOutline,
} from "react-icons/md";
import "./TodoListItem.scss";
import cn from "classnames";
import React from "react";

const TodoListItem = ({ todo, onRemove, onToggle, style }) => {
  const { id, text, checked } = todo;

  return (
    <div className="TodoListItem-virtualized" style={style}>
      <div className="TodoListItem">
        {/* class명이 checkbox 인것에 true이면 checked 가 클래스명이 추가.
                    class="checkbox checked" */}
        <div
          className={cn("checkbox", { checked })}
          onClick={() => onToggle(id)}
        >
          {/* checked가 체크가 되어있으면 true , 체크가 해제 되어있으면 false */}
          {checked ? <MdCheckBox /> : <MdCheckBoxOutlineBlank />}
          <div className="text">{text}</div>
        </div>
        <div className="remove" onClick={() => onRemove(id)}>
          <MdRemoveCircleOutline />
        </div>
      </div>
    </div>
  );
};

export default React.memo(TodoListItem);
