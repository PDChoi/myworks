c23456
      parameter(imax=1e7)
      real ra, dec, z, g1, r1, i1, g2, r2, i2, w
      real bin_min, bin_max, bin_num
      integer option, ncount
      character*50 filename


      filename = 'eBOSS_ELG.txt'

      bin_min = 0.
      bin_max = 2.
      bin_num = 20


      open(21, file = filename)
      open(22, file = 'z-histogram.txt')

      do j = 1, bin_num
      ncount = 0
      do i = 1, imax
      read(21, *, end=100) ra, dec, z, g1, r1, i1, g2, r2, i2, w

      if (z .gt. (bin_max - bin_min)/real(bin_num)*(j-1)) then
      if (z .le. (bin_max - bin_min)/real(bin_num)*j) then
       ncount = ncount + 1
      endif
      endif

      enddo
100   continue
      write(22, *) (bin_max - bin_min)/real(bin_num)*(j-1), ncount
      enddo
      
      stop
      end


c GNUPLOT:
c run -->
c xlabel 'z'
c ylabel 'number'
c p 'z-histogram.txt' w histeps lw 2 title 'ELG'
