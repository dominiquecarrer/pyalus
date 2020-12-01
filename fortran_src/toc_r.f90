Recursive Subroutine toc_r(errcode, errmsg, &
      & debuglevel , &
      & day_of_year, &
      & model, k_array, ck_array, &
      & toc_min, toc_max, &
      & sig_min, sig_max, &
      & latitude, tocxsize, tocysize, N_channels, MM, solzenith_out, &
      & tocr, tocr_cov)
    Use brdfmodels
    Implicit None
    Character (Len=1024) :: errmsg
    Integer :: errcode
    Integer, Intent(In)  :: model
    Integer, Intent (In) :: tocxsize
    Integer, Intent (In) :: tocysize
    Integer, Intent (In)   :: MM
    Integer, Intent (In)   :: N_channels
    Integer, Intent (In) :: debuglevel
    Integer, Intent (In) :: day_of_year     ! day of the year
    Real, Intent(In)  :: toc_min
    Real, Intent(In)  :: toc_max
    Real, Intent(In)  :: sig_min
    Real, Intent(In)  :: sig_max
    Real, Dimension (1:tocxsize, 1:tocysize), Intent(In):: latitude
    Real, Dimension (1:tocxsize, 1:tocysize, 1:N_channels, 0:MM), Intent(In):: k_array
    Real, Dimension (1:tocxsize, 1:tocysize, 1:N_channels, 0:MM, 0:MM), Intent(In):: ck_array
    Real, Dimension (1:tocxsize, 1:tocysize), Intent(InOut):: solzenith_out
    Real, Dimension (1:tocxsize, 1:tocysize, 1:N_channels), Intent(InOut):: tocr
    Real, Dimension (1:tocxsize, 1:tocysize, 1:N_channels), Intent(InOut):: tocr_cov
    Real, Dimension (0:MM) :: kernels_values
    !f2py intent(out) errmsg
    !f2py intent(out) errcode
    !f2py intent(in,hide) tocysize
    !f2py intent(in,hide) tocxsize
    !f2py intent(in,hide) N_channels
    !f2py intent(in,hide) MM

    Real, Parameter :: pi           = 3.141592653589793238462643383279502884197
    Real, Parameter :: epsilon_var  = 1.E-6

    Integer :: x,y,I,N,NN
    Real :: lat, theta_sol_10am, tocr_s, variance, sigma
    Real :: cov_aux
    Real, Dimension (0:MM, 0:MM):: ck
    Real :: nan, nanhelper
    nanhelper = 0.
    nan = nanhelper / nanhelper

    errcode = 0
    errmsg = ''

    Do y = 1, tocysize
        Do x = 1, tocxsize
            If (debuglevel .ge. 100) print *, '-----',x,y
            lat = latitude(x,y)

            Call solzenith(day_of_year, lat, theta_sol_10am,10.)
            theta_sol_10am = Minval( (/theta_sol_10am, 90. /) )
            solzenith_out(x,y) = theta_sol_10am
            !print *, 'latitude', lat
            If (debuglevel .ge. 101) print *, 'theta_sol_10am', theta_sol_10am
            If (debuglevel .ge. 101) print *, 'model', model
            kernels_values = brdfmodel(0., 0., theta_sol_10am * pi / 180., model)
            If (debuglevel .ge. 102) print *, 'kernels_values', kernels_values
            Do I = 1, N_channels
             tocr_s = Dot_Product(k_array(x,y,I,:), kernels_values)

             ! ensure covariance is good. Same numerical trick as in model_fit.f90
             Do N = 0, MM
                Do NN = N, MM
                   cov_aux = ck_array(x,y,I,N,NN)
                   ck(N,NN) = cov_aux**2
                   If ( N .eq. NN ) Then
                      ! assure positive variances
                      ck(N,N) = Maxval( (/ ck(N,N), epsilon_var /) )
                   Else
                      If ( cov_aux .lt. 0 ) ck(N,NN) = - ck(N,NN)
                      ! set co-variances to zero for numerical reasons
                      ck(N,NN) = 0. ! comment this line for using covariances
                      ck(NN,N) = ck(N,NN)
                   End If
                End Do
             End Do

             If (debuglevel .ge. 50) print *, '   ck = ',ck
             variance = Dot_Product(kernels_values,Matmul(ck,kernels_values))
             If (debuglevel .ge. 50) print *, '   kernels variance negative ', variance, ' setting to 0.'
             variance = Maxval( (/ variance, 0. /) )
             sigma = Sqrt( variance )
             sigma = Minval( (/sigma, sig_max/) )
             sigma = Maxval( (/sigma, sig_min/) )

             if ((tocr_s .lt. toc_min) .or. (tocr_s .gt. toc_max)) Then
                 If (debuglevel .ge. 50) print *, 'tocr_s out of limit ', tocr_s, ' setting to nan'
                 tocr_s = nan
                 sigma = nan
             end if
             If (debuglevel .ge. 100) print *, 'k012 ', k_array(x,y,I,:)
             If (debuglevel .ge. 100) print *, 'band', I, 'tocr spectral', tocr_s

             tocr(x,y,I) = tocr_s
             tocr_cov(x,y,I) = sigma
             If (debuglevel .ge. 100) print *, 'ck 012*012 ', ck_array(x,y,I,:,:)
             If (debuglevel .ge. 100) print *,I, 'tocr_cov spectral', sigma
            End Do
        End Do
    End Do
End Subroutine toc_r
