parseConfigError = '解析配置文件出错，请检查是否存在配置文件！'
findUserJsonFile = "找到user.json配置文件,将从配置文件中读取信息！"

# signCheck
signCheckStartTips = '----------------------------每日签到检查开始-----------------------------'
signCheckStartDesc = '          每日11点以及23点为打卡检查，此时间段内自动打卡不会运行          '
signCheckError = '每日签到检查运行错误！可能与服务器建立连接失败,具体错误原因：'
signCheckEndTips = '----------------------------每日签到检查完成-----------------------------'
signCheckError2 = '            获取用户打卡记录失败          '
signCheckRetroactiveStart = '            今日未打上班卡，准备补签          '
signCheckRetroactiveEnd = '            今日未打下班卡，准备补签          '
signCheckTips3 = '        Tips：如果没提示上班或者下班补签即代表上次打卡正常          '

# tokenSign
tokenSignWarning = '警告：保持登录失败，Token失效，请及时更新Token'
tokenSignRetry = '重试：正在准备使用账户密码重新签到'
tokenSignError = '工学云设备Token失效'
tokenSignErrorDesc = '工学云自动打卡设备Token失效，本次将使用账号密码重新登录签到，请及时更新配置文件中的Token,如不再需要保持登' \
                     '录状态,请及时将配置文件中的keepLogin更改为false取消保持登录打卡，如有疑问请联系邮箱：XuanRanDev@qq.com'

# sign
signError = '打卡失败，错误原因:'
signErrorNotifyTitle = '工学云打卡失败！'

# save
prepareSign = '-------------准备打卡--------------'
signFinish = '-------------打卡完成--------------'
signOK = '打卡成功'
signNo = '打卡失败'
