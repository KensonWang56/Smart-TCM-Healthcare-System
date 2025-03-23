// 密码验证规则
export function validatePassword(rule, value, callback) {
  // 密码长度至少8位
  if (value.length < 8) {
    callback(new Error('密码长度不能小于8位'))
    return
  }

  // 必须包含数字和字母
  const hasNumber = /\d/.test(value)
  const hasLetter = /[a-zA-Z]/.test(value)
  if (!hasNumber || !hasLetter) {
    callback(new Error('密码必须包含数字和字母'))
    return
  }

  // 可以包含特殊字符，但不允许空格
  if (/\s/.test(value)) {
    callback(new Error('密码不能包含空格'))
    return
  }

  callback()
} 