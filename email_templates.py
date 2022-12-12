def _default_template(avatarUrl, fullName, htmlContent):
    avatarDiv = '<br>'
    if avatarUrl:
        avatarDiv = f'''<img src="https://sergtyapkin.herokuapp.com/squest/api{avatarUrl}" height="80px" width="80px" alt="avatar" title="avatar" style="margin: 20px auto;border-radius: 40px"/>
            <br>
        '''

    fullNameDiv = ''
    if fullName:
        fullNameDiv = f'''<span style="font-weight: bold;font-size: 22px;color: #f3f3f3;">{fullName},</span>
            <br>
            <br>
        '''

    return f"""
    <div style="background: linear-gradient(-20deg,#b8860b 0%,#5b3509 20%,#1c051c 70%,#0e0909 100%);">
        <div style="margin-left: auto;margin-right: auto;width: 100%;max-width: 600px;padding:40px 0;font-family: Arial, sans-serif">
            <div style="margin: 40px 0;padding: 0 35px 25px;text-align: center;color: #d5d5d5;background: linear-gradient(20deg,#1c051c 0%,#5b3509 50%,#29190c 100%) 50% 50% no-repeat;box-shadow: 3px 3px 10px #000;border-radius: 7px;line-height: 1.3;font-size: 16px;">
                {avatarDiv}
    
                {fullNameDiv}
                
                <div class="content">
                    {htmlContent}
                </div>
                
                <br>
                <div style="padding: 0 15px;color: #aaa;font-size: 11px;text-align: center;">
                    <span>Ты получаешь это письмо, потому что этот адрес почты указапри регистрации на SQuest.</span>
                    <br>
                    <span>С этого электронного адреса приходят только важные письма для восстановления пароля, входа в аккаунт и.т.п.</span>
                </div>
            </div>
    
            <div style="padding: 20px 30px;color: #666;overflow: auto;background-color: #00000055;border-radius: 7px">
                <span style="float: left">
                    <a href="https://sergtyapkin.herokuapp.com/squest" target="_blank" style="font-size: 13px;font-weight: bold;color: #e7e7e7 !important;" rel=" noopener noreferrer">SQuest.ml</a>
                    <br>
                    <span style="color: #b9b9b9;font-size: 12px;">SQuest Ltd., ул. Пушкина, д. Колотушкина.</span>
                </span>
    
                <div style="float: right;padding: 8px 0 8px 20px;">
                    <span style="vertical-align: middle;padding-right: 10px;font-size: 13px;color: #b9b9b9;">Соцсети:</span>
                    <a style="margin-left: 5px;height: 22px;vertical-align: middle" href="https://vk.com/squest_studio" target="_blank" rel=" noopener noreferrer">
                        <img width="22px" height="22px" alt="vk" title="vk" src="https://sergtyapkin.herokuapp.com/squest/static/vk-logo.png"/>
                    </a>
                    <a style="margin-left: 5px;height: 22px;vertical-align: middle" href="https://t.me/tyapkin_s" target="_blank" rel=" noopener noreferrer">
                        <img width="22px" height="22px" alt="tg" title="tg" src="https://sergtyapkin.herokuapp.com/squest/static/tg-logo.png"/>
                    </a>
                </div>
            </div>
        </div>
    </div>
    """


def restorePassword(avatarUrl, fullName, code):
    return _default_template(avatarUrl, fullName, f"""
    <span style="color: #d5d5d5">пароль опять выпал из памяти, но ты очень хочешь попасть в свой аккаунт? Во-первых <b> пей таблетки</b>, и больше <b>не забывай</b> пароли.</span>
    <br>
    <br>
    <span style="color: #d5d5d5">А во-вторых - так и быть, держи сылку для восстановления пароля:</span>
    <br>
    <a href="https://sergtyapkin.herokuapp.com/squest/password/restore?code={code}" target="_blank" style="margin-top:10px;line-height: 1;box-sizing: border-box;display: inline-block;max-width: 100%;padding: 10px 15px;border-radius: 5px;background: linear-gradient(20deg,rgba(45,36,13,0.4) 0%,rgba(90,56,25,0.7) 50%,rgba(55,43,16,0.4) 100%) 50% 50% no-repeat;border: 1px #b08946 solid;box-shadow: inset 0 0 0 transparent, 5px 5px 10px rgb(0 0 0 / 33%);font-weight: bold;color: #fff !important;" rel=" noopener noreferrer"><span style="display: inline-block;width: 14px;height: 18px;vertical-align: middle;"></span> Восстановить пароль</a>
    <br>
    <span style="color: #d5d5d5">Кстати, она действительна всего час</span>    
    """)


def loginByCode(avatarUrl, fullName, code):
    return _default_template(avatarUrl, fullName, f"""
    <span style="color: #d5d5d5">неужели прям так лень запоминать пароль? Вот твой одноразовый код:</span>
    <br>
    <br>
    <div style="font-weight: bold;font-size: 25px;letter-spacing: 5px;color: #f3f3f3">{code}</div>
    <br>
    <span style="color: #d5d5d5">Кстати, он действителен всего час</span>     
    """)


def confirmEmail(avatarUrl, fullName, code):
    return _default_template(avatarUrl, fullName, f"""
    <span style="color: #d5d5d5">ну что за красивое личико смотрит на это письмо с той стороны экрана?</span>
    <br>
    <span style="color: #d5d5d5">Давай к делу - смотри, сколько всего тебе будет доступно после подтверждения этого адреса:</span>
    <br>
    <br>
    <hr>
    <div style="padding: 0 20px;font-size: 0;text-align: left;color: #c9c9c9">
        <div style="display: inline-block;width: 50%;min-width: 200px;vertical-align: top">
            <div style="color: #ff9b9b;box-sizing: border-box;white-space: nowrap;overflow:hidden;padding: 0;font-weight: normal;letter-spacing: 1px;font-size: 14px;">Без подтверждения:</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="https://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Просмотр квестов</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="https://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Прохождение заданий</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;">&nbsp;</div>
        </div>
        <div style="display: inline-block;width: 50%;min-width: 200px">
            <div style="color: #afff9c;box-sizing: border-box;white-space: nowrap;overflow:hidden;padding: 0;font-weight: normal;letter-spacing: 1px;font-size: 14px;">С подтверждением:</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="https://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Ты в рейтинге</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="https://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Создание квестов</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="https://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Создание команд</div>
            <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="https://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Оценка квестов</div>
        </div>
    </div>
    <hr>
    <br>
    <div style="margin-top: 20px;padding: 0 0 0 25px;text-transform: uppercase;font-weight: bold">Осталось только</div>
    <a href="https://sergtyapkin.herokuapp.com/squest/email/confirm?code={code}" target="_blank" style="margin-top:10px;line-height: 1;box-sizing: border-box;display: inline-block;max-width: 100%;padding: 10px 15px;border-radius: 5px;background: linear-gradient(20deg,rgba(45,36,13,0.4) 0%,rgba(90,56,25,0.7) 50%,rgba(55,43,16,0.4) 100%) 50% 50% no-repeat;border: 1px #b08946 solid;box-shadow: inset 0 0 0 transparent, 5px 5px 10px rgb(0 0 0 / 33%);font-weight: bold;color: #fff !important;" rel=" noopener noreferrer"><span style="display: inline-block;width: 14px;height: 18px;vertical-align: middle;"></span> Подтвердить регистрацию</a>
    <br>
    <br>
    <span>Ссылка для подтверждения действительна всего день</span>        
    """)
