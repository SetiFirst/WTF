import type  { FC }  from "react";

const Auth: FC = () => {
    return (
        <div className="auth-form">
            <form className="form" action="/auth/token" >
                <input name="login" type="text" placeholder="Логин" />
                <input name="password" type="password" placeholder="Пароль" />
                <button type="submit"> Войти </button>
                <div className="postscribe">
                    Нет аккаунта? <a href="/choice/">Регистрация</a>
                </div>
            </form>
        </div>
    );
};

export default Auth;
