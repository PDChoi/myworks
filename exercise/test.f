c23456
      character*15 path, path2
      write(path, '(A14)') 'aaaaaaaaaa'
      write(path2, '(A5, A10)') 'aaaaa', path
      print*, path, path2

      path = 'ssss
     *ssss'

      print*, path

      stop
      end
