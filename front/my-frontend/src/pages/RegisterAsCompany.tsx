import type  { FC }  from "react";

const RegisterAsPerson: FC = () => {
    return (
        <div className="auth-form choice-form">
            <form className="form" action="/auth/token" >
                <div className="title"> Регистрация </div>
                <input name="login" type="text" placeholder="Логин" />
                <input name="INN" type="text" placeholder="ИНН" />
                <input name="password" type="password" placeholder="Пароль" />
                <input name="password2" type="password" placeholder="Повторите пароль" />
                <button type="submit"> Зарегистрироваться </button>
            </form>
        </div>
    );
};

export default RegisterAsPerson;