    import {type FC, useState } from "react";
    import Search from "../Search";
import { NavLink } from "react-router-dom";

    const BottomMenu: FC = () => {

        const [search, setSearch] = useState(false);

        function openSearch() {
            setSearch(!search)
        }

        return(
            <>
                {
                    search ? (<Search search={search} setSearch={setSearch}/>) : ""
            }

            <div className="bottom-menu">
                <div className="allCourses">
                    <NavLink
                        to="/app/all-courses"
                        className={({ isActive }) => isActive ? "active" : ""}
                    >
                        <img src="/src/assets/ac.svg" alt="Все курсы" />
                    </NavLink>
                </div>

                <div className="searchCourses" onClick={openSearch}>
                    <img src="/src/assets/search.svg" alt="Поиск курсов" />
                </div>

                <div className="settings-icon">
                    <NavLink
                        to="/app/settings"
                        className={({ isActive }) => isActive ? "active" : ""}
                    >
                        <img src="/src/assets/settings.svg" alt="Настройки" />
                    </NavLink>
                </div>
            </div>


        </>
    );
}

export default BottomMenu;