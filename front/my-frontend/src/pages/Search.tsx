import { FC } from "react";
import List from "./Components/List";

interface SearchProps {
  search: boolean;
  setSearch: React.Dispatch<React.SetStateAction<boolean>>;
}


const Search: FC<SearchProps> = (props) => {

    const list = [
        { name: "Course 1", descr: "Description 1", courseID: "course1" },
        { name: "Course 2", descr: "Description 2", courseID: "course2" },
        { name: "Course 3", descr: "Description 3", courseID: "course3" }
    ];

    let search = props.search;
    let setSearch = props.setSearch;

    return(
        <>
            <div className="search">
                <div className="search__left"></div>
                <div className="search__string">
                    <input type="text" placeholder="Поиск"/>
                </div>
                <div className="search__exit">
                    <img src="/src/assets/exit.svg" alt="exit" onClick={() => setSearch(!search)} />
                </div>
                <div className="search-courses">
                    <List list={list}/>
                </div>
                <div className="search__right"></div>
            </div>
        </>
    );
}

export default Search;