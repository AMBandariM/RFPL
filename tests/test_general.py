# This is a general test and not a edge test. It will test the normal
# usage of RFPL, making sure core features are not broken. Although
# edge tests are also useful, RFPL is changing rapidly and it would be
# tedious to manage tests.

import unittest
from typing import Union

from rfpl.interpreter import Interpreter, Message, MessageType
from rfpl.natural import Natural

class GeneralTestCase(unittest.TestCase):
    def setUp(self):
        self.intr: Interpreter = Interpreter()

    def assertOk(self, line: str) -> list[Message]:
        ok, messages = self.intr.report(line)
        for msg in messages:
            self.assertTrue(
                msg.typ not in (MessageType.ERROR, MessageType.EXCEPTION),
                f'"{line}" reported: {msg.message}'
            )
        self.assertTrue(ok, f'"{line}" returned not ok')
        return messages

    def Natural(self, natrepr: Union[int, list, None]):
        if isinstance(natrepr, list):
            return Natural([self.Natural(n) for n in natrepr])
        return Natural(natrepr)
    
    def assertReturns(self, line: str, expect):
        expect = self.Natural(expect)
        messages = self.assertOk(line)
        for msg in messages:
            if msg.typ == MessageType.NATURAL:
                self.assertTrue(msg.natural == expect, f'"{line}" returned {msg.natural}, expected {expect}')

    def test_add_mul(self):
        self.assertOk('add = Pr[!0, Cn[S, !0]]')
        self.assertReturns('add(2, 3)', 5)
        self.assertOk('mul = Pr[#0, Cn[add, !0, !2]]')
        self.assertReturns('mul(3, 2)', 6)
    
    def test_factor(self):
        self.assertOk('load inflist')
        self.assertReturns('factor(100, 1023)', [3, [3, 1], [11, 1], [31, 1]])
        self.assertOk('load parsa-fib')
        self.assertOk('fibs = imap[get0, fib]')
        self.assertReturns('scanl[scanr[fibs]](7)', [7, [], [1], [2, 1], [3, 1, 1], [4, 2, 1, 1], [5, 3, 2, 1, 1], [6, 5, 3, 2, 1, 1]])

    def test_lazy(self):
        self.assertOk('load logic')
        self.assertReturns('if[#1, !0, #_](10)', 10)
        self.assertReturns('if[#0, #_, !1](_, 11)', 11)

    def test_stack(self):
        self.assertOk('load stack')
        self.assertOk('a = Cn[append, #<3, 1, 2>, #11]')
        self.assertReturns('a()', [4, 1, 2, 0, 11])
        self.assertReturns('map[S](a())', [4, 2, 3, 1, 12])
        self.assertOk('load logic')
        self.assertOk('even = Cn[not, Cn[Mod, !0, #2]]')
        self.assertReturns('filter[even](a())', [2, 2, 0])


if __name__ == '__main__':
    unittest.main()
