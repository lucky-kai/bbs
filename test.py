from utils import log


def is_right_email(s):
    # if '@' not in s:
    #     log('邮箱格式不正确')
    #     return False
    # else:
    #     return True
    return '@' in s and '.com' == s[len(s) - 4:]


def test_email():
    email = 'luckyKailin@gmail.com'
    return is_right_email(email)


def test():
    print('Hello World    ')
    print('Hello World    ')
    print('Hello World    ')




if __name__ == '__main__':
    # log(test_email())
    test()




