Recursive Subroutine is_nan (errcode, errmsg, debuglevel, &
      & acf, &
      & input)

  !Use algoconf
  !se brdfmodels
      Implicit None

      Character (Len=1024) :: errmsg
      Integer :: errcode

      Character(LEN=255), Intent(In) :: acf
      Integer, Intent (In) :: debuglevel

      REAL (Kind=4), Intent(InOut) :: input
      !Integer (Kind=2), Dimension(1:2,1:2), Intent(InOut) :: brdf

    !f2py intent(out) errmsg
    !f2py intent(out) errcode
    !f2py threadsafe
    errmsg = ''
    print *,acf
    if ((isnan(input))) then
    !if ((input .ne. input)) then
        print *, input , ' is a nan'
        errcode = 0
    else
        print *, input
        errcode = 1
    end if
    print *, 'debuglevel', debuglevel

End Subroutine is_nan
