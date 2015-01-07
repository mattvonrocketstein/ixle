""" ixle.tests.test_heuristics
"""
import sys
from unittest2 import TestCase

from ixle.tests.common import make_mp3, make_subtitles, make_movie, make_tv
from ixle.heuristics import is_tagged, is_movie, guess_movie_year, guess_movie_name
from report import report

class TestMovie(TestCase):

    def setUp(self):
        self.mp3 = make_mp3()
        self.subtitles = make_subtitles()
        self.movie = make_movie()
        self.tv1 = make_tv()
        self.tv2 = make_tv(size=sys.maxint)

    def test_ID3_implies_tagged(self):
        assert is_tagged(self.mp3)

    def test_subtitles_are_NOT_movie(self):
        assert not is_movie(self.subtitles)

    def test_guess_movie_name(self):
        movie = self.movie
        assert guess_movie_name(movie)=='Network'
        movie = make_movie(id='Argo.2012.WEBRip.READNFO.XviD-RESiSTANCE.avi')
        assert guess_movie_name(movie)=='Argo'
        movie = make_movie(id='Cloud.Atlas.2012.R5.CAM.AUDiO.READNFO.XviD-RESiSTANCE.avi')
        assert guess_movie_name(movie)=='Cloud Atlas'
        movie = make_movie(id='2006 - Jet.Li.Fearless.cd1-Eng.avi')
        assert guess_movie_name(movie)=='Jet Li Fearless'

    def test_guess_movie_year(self):
        assert guess_movie_year(self.movie)=='1976'
        assert guess_movie_year(self.subtitles)==None
        assert guess_movie_year(self.tv1)==None
        assert guess_movie_year(self.tv2)==None
        movie = make_movie(id='Cloud.Atlas.2012.R5.CAM.AUDiO.READNFO.XviD-RESiSTANCE.avi')
        assert guess_movie_year(movie)=='2012'
        movie = make_movie(id='2006 - Jet.Li.Fearless.cd1-Eng.avi')
        assert guess_movie_year(movie)=='2006'

    def test_movie(self):
        assert is_movie(self.movie)

    def test_tv_not_movie(self):
        assert not is_movie(self.tv1)

    def test_HUGE_tv_still_not_movie(self):
        assert not is_movie(self.tv2)
