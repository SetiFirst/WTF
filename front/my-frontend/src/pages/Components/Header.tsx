import type { FC } from "react";

const Header: FC = () => {
    
    return (
        <>
            <header className="header">
                <div>
                    <div className="profile">
                        <img src="/src/assets/profile.svg"/>
                    </div>
                </div>
                <div className="bonuses">
                    <div className="exp">123xp<img src="/src/assets/exp.svg"/></div>
                    <div className="money">123<img src="/src/assets/money.svg"/></div>
                    <div className="streak">123<img src="/src/assets/burn.svg"/></div>
                </div>
            </header>
        </>
    );
}

export default Header;