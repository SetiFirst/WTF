import type { FC } from "react";
import List from "./Components/List.tsx";

const AllCourses: FC = () => {
  const list = [
    { name: "Course 1", descr: "Description 1", courseID: "course1", url:"/app/course?courseID=course1"},
    { name: "Course 2", descr: "Description 2", courseID: "course2", url:"/app/course?courseID=course2"},
    { name: "Course 3", descr: "Description 3", courseID: "course3", url:"/app/course?courseID=course3"}
  ];

  return (
    <div className="all-courses">
      <div>
        <div className="title center">Все курсы</div>
        <List list={list} />
      </div>
    </div>
  );
};

export default AllCourses;
