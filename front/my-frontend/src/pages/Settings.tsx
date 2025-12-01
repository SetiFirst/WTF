import type { FC } from "react";
import List from "./Components/List.tsx";

const Settings: FC = () => {
  const list = [
    { name: "Режим создания сайта", descr: "", img:"/src/assets/ccm.svg" },
    { name: "Тема", descr: "", img:"/src/assets/toggle-on.svg" },
    { name: "Чтото ещё", descr: "", img:"/src/assets/bug.svg" }
  ];

  return (
    <div className="settings">
      <div>
        <div className="title center">Настройки</div>
        <List list={list} />
      </div>
    </div>
  );
};

export default Settings;
