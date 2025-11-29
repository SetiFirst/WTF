import type { FC } from "react";

interface ListProps {
  list: Array<{ id?: number; name: string; descr: string, img?: string, courseID?: string, url?: string}>;
}

const List: FC<ListProps> = ({ list }) => {
  return (
    <ul className="list">
      {list.map((el, index) => (
        <li key={el.id ?? index} id={el.courseID}>
          <a href={el.url}>
            {
              el.img ? (
                <div className="img">
                  <img src={el.img} alt={el.name} />
                </div>
              ) : ""
            }
            <div className="text">
              <h2>{el.name}</h2>
              <p>{el.descr}</p>
            </div>
          </a>
        </li>
      ))}
    </ul>
  );
};

export default List;
