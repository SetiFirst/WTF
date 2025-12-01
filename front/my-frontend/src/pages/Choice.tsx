import type  { FC }  from "react";

const Choice: FC = () => {
    return (
        <div className="auth-form choice-form">
            <div className="form">
                <div className="title">Кем вы являетесь?</div>
                <a className="button" href="/register-as-person/">Физ. лицо</a>
                <a className="button" href="/register-as-company/">Юр. лицо</a>
            </div>
        </div>
    );
};

export default Choice;
