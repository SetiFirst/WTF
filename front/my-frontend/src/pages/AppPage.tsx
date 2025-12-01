import { Outlet } from "react-router-dom";
import Header from "./Components/Header";
import BottomMenu from "./Components/BottomMenu";

const AppPage = () => {
  return (
    <>
      <Header />

      <main className="content">
        <Outlet />
      </main>

      <BottomMenu />
    </>
  );
};

export default AppPage;
