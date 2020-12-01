Recursive Subroutine solzenith(day,lat,zenith, localhour)
  ! based on the routine zensun.pro by Paul Ricchiazzi (Earth Space Research Group, UCSB)
  Implicit None
  Real, Intent(In)     :: localhour ! local hour of the day (noon=12. 10am=10. 1am=13.  etc.)
  Integer, Intent(In)  :: day       ! day of the year
  Real, Intent(In)     :: lat       ! geographic latitude of point on earth's surface (degrees)
  Real, Intent(Out)    :: zenith    ! solar zenith angle (degrees)

  Integer, Parameter :: np = 74

  Real, Dimension(1:np), Parameter :: nday = &
       & (/  1.0,   6.0,  11.0,  16.0,  21.0,  26.0,  31.0,  36.0,  41.0,  46.0,&
       &    51.0,  56.0,  61.0,  66.0,  71.0,  76.0,  81.0,  86.0,  91.0,  96.0,&
       &   101.0, 106.0, 111.0, 116.0, 121.0, 126.0, 131.0, 136.0, 141.0, 146.0,&
       &   151.0, 156.0, 161.0, 166.0, 171.0, 176.0, 181.0, 186.0, 191.0, 196.0,&
       &   201.0, 206.0, 211.0, 216.0, 221.0, 226.0, 231.0, 236.0, 241.0, 246.0,&
       &   251.0, 256.0, 261.0, 266.0, 271.0, 276.0, 281.0, 286.0, 291.0, 296.0,&
       &   301.0, 306.0, 311.0, 316.0, 321.0, 326.0, 331.0, 336.0, 341.0, 346.0,&
       &   351.0, 356.0, 361.0, 366.0 /)

  Real, Dimension(1:np), Parameter :: dec = &
       & (/ -23.06,-22.57,-21.91,-21.06,-20.05,-18.88,-17.57,-16.13,-14.57,-12.91,&
       &    -11.16, -9.34, -7.46, -5.54, -3.59, -1.62,  0.36,  2.33,  4.28,  6.19,&
       &      8.06,  9.88, 11.62, 13.29, 14.87, 16.34, 17.70, 18.94, 20.04, 21.00,&
       &     21.81, 22.47, 22.95, 23.28, 23.43, 23.40, 23.21, 22.85, 22.32, 21.63,&
       &     20.79, 19.80, 18.67, 17.42, 16.05, 14.57, 13.00, 11.33,  9.60,  7.80,&
       &      5.95,  4.06,  2.13,  0.19, -1.75, -3.69, -5.62, -7.51, -9.36,-11.16,&
       &    -12.88,-14.53,-16.07,-17.50,-18.81,-19.98,-20.99,-21.85,-22.52,-23.02,&
       &    -23.33,-23.44,-23.35,-23.06 /)

  Real, Parameter :: dtor = 0.017453292

  Real :: tt, decang, latsun, lonsun
  Real :: t0, t1, zz, alpha

  Integer :: I, J

  ! compute the subsolar coordinates

  tt = Modulo( day+localhour/24.-1., 365.25) + 1.  ! fractional day number with 12am 1jan = 1.

  I = Count(nday .le. tt)                     ! linear interpolation in the tables above
  If (I .lt. np) Then
     J = I + 1
     alpha = (tt-nday(I)) / (nday(J)-nday(I))  
  Else
     J = I
     alpha = 0.
  End If
  decang = (1.-alpha)*dec(I) + alpha*dec(J)
  latsun = decang

  ! compute the solar zenith

  t0 = (90.-lat)*dtor                             ! colatitude of point
  t1 = (90.-latsun)*dtor                          ! colatitude of sun

  zz = Cos(t0)*Cos(t1)+Sin(t0)*Sin(t1) 

  zenith  = Acos(zz)/dtor                         ! solar zenith

End Subroutine solzenith
