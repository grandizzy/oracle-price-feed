# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2020 grandizzy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

from pymaker import Address


class Config:
    def __init__(self, oracle_address: Address, token: str, report_time: int, fetch_time: int, ro_account: Optional[str], rw_account: Optional[str]):

        assert(isinstance(oracle_address, Address))
        assert(isinstance(token, str))
        assert(isinstance(report_time, int))
        assert(isinstance(fetch_time, int))
        assert(isinstance(ro_account, str) or ro_account is None)
        assert(isinstance(rw_account, str) or rw_account is None)

        self.oracle_address = oracle_address
        self.token = token
        self.ro_account = ro_account
        self.rw_account = rw_account
        self.report_time = report_time
        self.fetch_time = fetch_time
