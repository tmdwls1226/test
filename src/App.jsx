import React, { useCallback, useReducer, useRef, useState } from "react";
import TodoTemplate from "./components/TodoTemplate";
import TodoInsert from "./components/TodoInsert";
import TodoList from "./components/TodoList";

function createBulkTodos() {
  const array = [];
  for (let i = 1; i <= 3000; i++) {
    array.push({
      id: i,
      text: `할 일 ${i}`,
      checked: false,
    });
  }
  return array;
}

function todoReducer(todos, action) {
  switch (action.type) {
    case "INSERT": //새로추가
      //{type : 'INSERT', todo:{id:1, text:'todo', checked:false}}
      return todos.concat(action.todo);
    case "Remove": //제거
      //{type: 'Remove',id:1'}
      return todos.filter((todo) => todo.id !== action.id);
    case "TOGGLE": //토글
      //{type: 'REMOVE, id:1'}
      return todos.map((todo) =>
        todo.id === action.id ? { ...todo, checked: !todo.checked } : todo,
      );
    default:
      return todos;
  }
}

function App() {
  //두번째에 undefined을 넣고, 세번째 파라미터에 초기 상태를 만드는 함수 createBulkTodos을 넣으면
  // 컴포넌트가 처음렌더링 될때만 createBulkTodos함수를 호출된다
  const [todos, dispatch] = useReducer(todoReducer, undefined, createBulkTodos);

  // 고유값으로 사용될 id
  // ref를 사용하여 변수 담기
  // 변경이 잦은 변수를 담는공간
  const nextId = useRef(3001);

  const onInsert = useCallback(
    // onInsert = 데이터삽입
    (text) => {
      const todo = {
        id: nextId.current,
        text,
        checked: false,
      };
      dispatch({ type: "INSERT", todo });
      //nextId.current=nextId.current+1
      nextId.current += 1; //nextId 1씩 더하기
    },
    [],
  );

  const onRemove = useCallback((id) => {
    dispatch({ type: "REMOVE", id }); //id값을 받아 지운 id랑 다르면 남겨라
  }, []);

  const onToggle = useCallback((id) => {
    dispatch({ type: "TOGGLE", id });
  }, []);

  return (
    <TodoTemplate>
      <TodoInsert onInsert={onInsert} />
      <TodoList todos={todos} onRemove={onRemove} onToggle={onToggle} />
    </TodoTemplate>
  );
}

export default App;
