Recursive Subroutine albedo_angular_integration (errcode, errmsg, debuglevel,&
      & square_my_input_variance, &
      & k_array, &
      & Ck_array, &
      & latitude, longitude, &
      & debuginfo, &
      & snow_mask_out, &
      & model , &
      & theta_ref_dh_limit, &
      & theta_sol_midi_limit, &
      & day_of_year, &
      & alb_max, &
      & alb_min, &
      & sig_max, &
      & sig_min, &
      & cxx_max ,& !cxx_min, &
      & cxy_max ,cxy_min, &
      & albedos, albedos_cov, & 
      & xstart, xend, ystart, yend, &
      & MSGpixX, Lines, MM, N_channels, &
      & n_debuginfo, &
      & age, albedos_age, &
      & quality, albedos_quality)

    Use algoconf
    Use brdfmodels
    Implicit None

    Integer, Parameter   :: N_albedos = 2
    Character (Len=1024) :: errmsg
    Integer              :: errcode

    Integer, Intent(In)  :: model
    Integer, Intent(In)  :: debuglevel ! should be set to 0
    Logical, Intent(In)  :: square_my_input_variance ! see README "variance sqrt in angular integration module"

    ! Matrices dimensions
    Integer, Intent(In)   :: N_channels
    Integer, Intent(In)   :: Lines
    Integer, Intent(In)   :: MSGpixX
    Integer, Intent(In)   :: MM
    Integer, Intent(in)   :: n_debuginfo

    Integer, Intent(In) :: xstart, xend, ystart, yend ! window to process
    Real, Intent(In) :: alb_max    ! maximum value for albedo
    Real, Intent(In) :: alb_min    ! minimum value for albedo
    Real, Intent(In) :: sig_max    ! maximum value for albedo error
    Real, Intent(In) :: sig_min    ! minimum value for albedo error
    Real, Intent(In) :: cxx_max    ! maximum value for diagonal covariance matrix elements
    !Real, Intent(In) :: cxx_min    ! minimum value for diagonal covariance matrix elements
    Real, Intent(In) :: cxy_max    ! maximum value for other covariance matrix elements
    Real, Intent(In) :: cxy_min    ! minimum value for other covariance matrix elements


    Real(Kind=realkind), Intent (In) :: theta_ref_dh_limit
    Real(Kind=realkind), Intent (In) :: theta_sol_midi_limit
    Integer,              Intent (In) :: day_of_year

    ! input brdf data
    Real (Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels,0:MM),       Intent(In) :: k_array
    Real (Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels,0:MM, 0:MM), Intent(In) :: Ck_array
    Real(Kind=realkind), Dimension(1:MSGpixX, 1:Lines),                    Intent(In) :: latitude
    Real(Kind=realkind), Dimension(1:MSGpixX, 1:Lines),                    Intent(In) :: longitude
    Integer(Kind=realkind), Dimension(1:n_debuginfo),                           Intent(In) :: debuginfo
    Integer(Kind=quakind), Dimension(1:MSGpixX,1:Lines,1:N_channels),     Intent(In) :: age
    Integer(Kind=quakind), Dimension(1:MSGpixX,1:Lines,1:N_channels),     Intent(In) :: quality

    ! Output spectral albedo data
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_channels,1:N_albedos), Intent(InOut) :: albedos
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_channels,1:N_albedos), Intent(InOut) :: albedos_cov
    Integer(Kind=quakind), Dimension(1:MSGpixX,1:Lines,1:N_channels),    Intent(InOut) :: albedos_age
    Integer(Kind=quakind), Dimension(1:MSGpixX,1:Lines,1:N_channels),    Intent(InOut) :: albedos_quality
    Integer (Kind=1), Dimension(1:MSGpixX, 1:Lines),                     Intent(InOut) :: snow_mask_out

    !f2py intent(in,hide) n_debuginfo
    !f2py intent(in,hide) N_channels
    !f2py intent(in,hide) Lines
    !f2py intent(in,hide) MSGpixX
    !f2py intent(in,hide) MM
    !f2py intent(out) errmsg
    !f2py intent(out) errcode

    ! local variables
    Real :: theta_sol_midi  ! solar zenith angle at local solar noon
    Real :: theta_ref_dh    ! reference angle for dir.-hem. albedo
    Real :: alpha           ! auxiliary variable for linear interpolation
    Real (Kind=4), Dimension(0:MM)       :: k
    Real (Kind=4), Dimension(0:MM,0:MM)  :: Ck
    Integer                              :: X,Y,T,I,N, NN
    Real(Kind=realkind)                 :: lat
    Real, Dimension(0:MM)                :: dihi_calc 
    Real                                 :: tmp

    errcode = 0
    errmsg = ''

    If (debuglevel .ge. 10) print *, '---------------'
    If (debuglevel .ge. 10) print *, 'Entering albedo_angular_integration.f90'

    Call brdfinit(model) ! define integral tables according to model used

     Do I = 1, N_channels
        If (debuglevel .ge. 150) print *, 'Channel', I
        Do Y = ystart, yend
           Do X = xstart, xend
              If (debuglevel .ge. 100) print *, '--- Pixel Loop --- YX=',Y,X,'lat/lon = ',latitude(X,Y),longitude(X,Y)
              If (debuglevel .ge. 100) print *, '--- ',debuginfo
              If (snow_mask_out(X,Y) .eq. 0) then
                  If (debuglevel .ge. 150) print *, 'skipping in spectral integration because mask is 0',X,Y
                  If (debuglevel .ge. 150) print *, 'albedos = ', albedos(X,Y,I,:)
                  albedos_quality(X,Y,I) = quality(X,Y,I)
                  albedos_age(X,Y,I) = age(X,Y,I)
                  ! albedos(X,Y,I,:) = nan
                  ! albedos_cov(X,Y,I,:) = nan
                  cycle
              End If

              k = k_array(X,Y,I,:)
              lat = latitude(X,Y)
              Ck = Ck_array(X,Y,I,:,:)

              ! hack square_my_input_variance : see README "variance sqrt in angular integration module". TODO-latter : remove this ?
              If (square_my_input_variance) Then
                Do N = 0, MM
                   tmp = Ck(N,N)
                   If (.not. (isnan(tmp))) Then
                     tmp = tmp**2
                     tmp = Minval( (/tmp, cxx_max /) )
                   End If
                   Ck(N,N) = tmp
                End Do
                Do N = 0, MM-1
                   Do NN = N+1, MM
                      tmp = Ck(N,NN)
                      tmp = Sign(tmp **2, tmp)
                      tmp = Minval( (/tmp, cxy_max/) )
                      tmp = Maxval( (/tmp, cxy_min/) )
                      Ck(NN,N) = tmp
                      Ck(N,NN) = tmp
                   End Do
                End Do
              End If ! End-of hack square_my_input_variance

              ! determine solar angle at local solar noon : (noon = 12.)
              If (debuglevel .ge. 600) print *, 'theta_sol_midi : day_of_year ', day_of_year
              If (debuglevel .ge. 600) print *, 'theta_sol_midi : lat ', lat
              Call solzenith(day_of_year, lat, theta_sol_midi, 12.)
              theta_ref_dh = Minval( (/theta_sol_midi, theta_ref_dh_limit, 90. /) )
              ! linear interpolation in look-up-table
              T = Int( theta_ref_dh/theta_step )
              alpha = theta_ref_dh/theta_step - T
              If ( T .ge. n_table-1 ) Then
                 T = n_table-2
                 alpha = 1.
              End If
              dihi_calc(0) = 1.
              dihi_calc(1) = (1.-alpha)*hint(T,1) + alpha*hint(T+1,1)
              dihi_calc(2) = (1.-alpha)*hint(T,2) + alpha*hint(T+1,2)

              If (debuglevel .ge. 150) print *, 'nan ?', k,'.', albedos_quality(X,Y,:)
              If (isnan(k(1))) Then
                  If (debuglevel .ge. 150) print *, 'k(1) is nan'
                  snow_mask_out(X,Y) = 0 ! something is wrong with the coefficients : do not process further
                  albedos_quality(X,Y,I) = quality(X,Y,I) ! but propagate the quality flag (for historical reasons : TODO : clarify why)
              End If
              If (debuglevel .ge. 150) print *, 'theta_sol_midi', theta_sol_midi, theta_sol_midi_limit
              If ((theta_sol_midi .gt. theta_sol_midi_limit) .or. isnan(theta_sol_midi))  Then
                  If (debuglevel .ge. 15) print *,'  theta_sol_midi > theta_sol_midi_limit : skip', theta_sol_midi, theta_sol_midi_limit
                  snow_mask_out(X,Y) = 0 ! theta_sol_midi to high : do not process further
                  ! albedos_quality(X,Y,I) = quality(X,Y,I) ! and don't propagate the quality flag (for historical reasons : TODO : clarify why)
                  Cycle
              End If

              albedos_age(X,Y,I) = age(X,Y,I)
              albedos_quality(X,Y,I) = quality(X,Y,I)

              If (debuglevel .ge. 150) print *, '  k.', k
              If (debuglevel .ge. 150) print *, '  dihi_calc', dihi_calc
              If (debuglevel .ge. 150) print *, '  bihi_calc', bihi_calc

              ! calculate di-hemispherical albedo
              tmp = Dot_Product(k, dihi_calc)
              If (.not. (isnan(tmp))) Then ! If Dot_Product output nan, propagate it
                tmp = Minval( (/ tmp, alb_max/) )
                tmp = Maxval( (/ tmp, alb_min/) )
              End If
              albedos(X,Y,I,1) = tmp

              ! calculate bi-hemispherical albedo
              tmp = Dot_Product(k, bihi_calc)
              If (.not. (isnan(tmp))) Then
                tmp = Minval( (/ tmp, alb_max/) )
                tmp = Maxval( (/ tmp, alb_min/) )
              End If
              albedos(X,Y,I,2) = tmp

              If (debuglevel .ge. 150) print *, '  albedo dh ', tmp

              ! calculate di-hemispherical albedo covariance from the covariance matrix of the parameter errors
              ! sigma = Sqrt( I^T C I)
              tmp = Dot_Product(dihi_calc,Matmul(Ck,dihi_calc))
              If (.not. (isnan(tmp))) Then
                tmp = Sqrt( Maxval( (/ tmp, 0. /) ))
                tmp = Minval( (/ tmp, sig_max/) )
                tmp = Maxval( (/ tmp, sig_min/) )
              End If
              albedos_cov(X,Y,I,1) = tmp

              ! calculate bi-hemispherical albedo covariance from the covariance matrix of the parameter errors
              ! sigma = Sqrt( I^T C I)
              tmp = Dot_Product(bihi_calc,Matmul(Ck,bihi_calc))
              If (.not. (isnan(tmp))) Then
                tmp = Sqrt( Maxval( (/ tmp, 0. /) ))
                tmp = Minval( (/ tmp, sig_max/) )
                tmp = Maxval( (/ tmp, sig_min/) )
              End If
              albedos_cov(X,Y,I,2) = tmp

              If (debuglevel .ge. 150) print *, '  albedos=', albedos(X,Y,I,:)
              If (debuglevel .ge. 150) print *, '  albedo_cov=', albedos_cov(X,Y,I,:)
           End Do
        End Do
    End Do
End Subroutine albedo_angular_integration
