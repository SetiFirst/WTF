import { FC } from "react"
import { parseSearchParams } from "../utils/parseSearchParams";
import List from "./Components/List";

const Course: FC = () => {

    let searchParams = parseSearchParams(location.search);

    console.log(searchParams[0].value);

    const courseName = searchParams[0].value;

    const list = [
            { name: "Урок 1", descr: "Такойто такойто 1", },
            { name: "Урок 2", descr: "Такойто такойто 2", },
            { name: "Урок 3", descr: "Такойто такойто 3", }
    ];

    return(
        <>
            <div className="course">
                <div className="course-data">
                    <div className="title">{courseName}</div>
                    <div className="course-descr">
                        ОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписаниеОписание
                    </div>
                    <p className="title">Список уроков:</p>
                    <List list={list} />
                </div>
                <div className="course-data__shorty">
                    <div className="course-data__image"></div>
                    <div className="course-data__text">
                        <div className="course-data__author">Автор</div>
                        <div className="course-data__difficulty">Сложность</div>
                        <div className="course-data__time">Время прохождения</div>
                        <div className="course-data__type">Тип</div>
                    </div>
                </div>
            </div>

        </>
    );

}

export default Course;