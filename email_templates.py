def _default_template(avatarUrl, fullName, htmlContent):
    avatarDiv = '<br>'
    if avatarUrl:
        avatarDiv = f'''<img src="http://creativetechteam.bmstu.ru/api{avatarUrl}" height="80px" width="80px" alt="avatar" title="avatar" style="margin: 20px auto;border-radius: 40px"/>
            <br>
        '''

    fullNameDiv = ''
    if fullName:
        fullNameDiv = f'''<span style="font-weight: bold;font-size: 22px;color: #f3f3f3;">{fullName},</span>
            <br>
            <br>
        '''

    return f"""
    <div style="background: linear-gradient(-20deg, #111111 0%, #00f8fe 50%, #111111 100%);">
      <div style="margin-left: auto;margin-right: auto;width: 100%;max-width: 600px;padding:40px 0;font-family: Arial, sans-serif">
        <div style="margin: 40px 0;padding: 0 35px 25px;text-align: center;color: #d5d5d5;background: linear-gradient(60deg,#2f2f2f 0%, #2b3d39 100%) 50% 50% no-repeat;box-shadow: 3px 3px 10px #000;border-radius: 7px;line-height: 1.3;font-size: 16px;">
    
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
            <a href="http://creativetechteam.bmstu.ru" target="_blank" style="font-size: 13px;font-weight: bold;color: #e7e7e7 !important;" rel=" noopener noreferrer">CreativeTechTeam.bmstu.ru</a>
            <br>
            <span style="color: #b9b9b9;font-size: 12px;">Сергей Тяпкин</span>
          </span>
    
          <div style="float: right;padding: 8px 0 8px 20px;">
            <span style="vertical-align: middle;padding-right: 10px;font-size: 13px;color: #b9b9b9;">Соцсети:</span>
            <a style="margin-left: 5px;height: 22px;vertical-align: middle" href="http://vk.com/tyapkin_s" target="_blank" rel=" noopener noreferrer">
              <img width="22px" height="22px" alt="vk" title="vk" src="http://sergtyapkin.herokuapp.com/squest/static/vk-logo.png"/>
            </a>
            <a style="margin-left: 5px;height: 22px;vertical-align: middle" href="http://t.me/tyapkin_s" target="_blank" rel=" noopener noreferrer">
              <img width="22px" height="22px" alt="tg" title="tg" src="http://sergtyapkin.herokuapp.com/squest/static/tg-logo.png"/>
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
    <a href="http://creativetechteam.bmstu.ru/password/restore?code={code}" target="_blank" style="margin-top:10px;line-height: 1;box-sizing: border-box;display: inline-block;max-width: 100%;padding: 10px 15px;border-radius: 5555px;background: #444;border: #1a795f solid 1px;box-shadow: 5px 5px 10px rgb(0 0 0 / 27%);font-weight: bold;color: #b1e5df !important;" rel=" noopener noreferrer"><span style="display: inline-block;width: 14px;height: 18px;vertical-align: middle;"></span> Восстановить пароль</a>
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
    <span style="color: #d5d5d5">Надо подтвердить этот адрес, чтобы мы могли на законных основаниях слать тебе любой спам на эту почту :)</span>
    <br>
    <br>
    <hr>
    <div style="padding: 0 20px;font-size: 0;text-align: left;color: #c9c9c9">
      <div style="display: inline-block;width: 50%;min-width: 200px;vertical-align: top">
        <div style="color: #ff9b9b;box-sizing: border-box;white-space: nowrap;overflow:hidden;padding: 0;font-weight: normal;letter-spacing: 1px;font-size: 14px;">Без подтверждения:</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="http://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Не восстановишь пароль</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="http://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Минус один миска рис</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;">&nbsp;</div>
      </div>
      <div style="display: inline-block;width: 50%;min-width: 200px">
        <div style="color: #afff9c;box-sizing: border-box;white-space: nowrap;overflow:hidden;padding: 0;font-weight: normal;letter-spacing: 1px;font-size: 14px;">С подтверждением:</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="http://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Ты в рейтингах</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="http://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Ты лучший техпод в мире</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="http://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Все парни ArtClub'а твои</div>
        <div style="box-sizing: border-box;white-space: nowrap;padding: 0;font-weight: bold;font-size: 16px;"><img width="16px" height="16px" alt="+" title="+" style="margin-right: 5px" src="http://sergtyapkin.herokuapp.com/squest/static/ok.png"/>Хочу пицццу</div>
      </div>
    </div>
    <hr>
    <br>
    <div style="margin-top: 20px;padding: 0 0 0 25px;text-transform: uppercase;font-weight: bold">Осталось только</div>
    <a href="http://creativetechteam.bmstu.ru/email/confirm?code={code}" target="_blank" style="margin-top:10px;line-height: 1;box-sizing: border-box;display: inline-block;max-width: 100%;padding: 10px 15px;border-radius: 5555px;background: #444;border: #1a795f solid 1px;box-shadow: 5px 5px 10px rgb(0 0 0 / 27%);font-weight: bold;color: #b1e5df !important;" rel=" noopener noreferrer"><span style="display: inline-block;width: 14px;height: 18px;vertical-align: middle;"></span> Подтвердить регистрацию</a>
    <br>
    <br>
    <span>Ссылка для подтверждения действительна всего день</span>    
    """)
