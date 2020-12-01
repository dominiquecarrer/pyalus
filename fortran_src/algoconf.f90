Module algoconf
  Integer, Parameter :: refkind = 2
  Integer, Parameter :: maskind = 1
  Integer, Parameter :: angkind = 2
  Integer, Parameter :: latkind = 2
  Integer, Parameter :: lwmkind = 1
  Integer, Parameter :: inkind  = 2
  ! in/output data variables
  Integer, Parameter :: parkind = 2
  Integer, Parameter :: covkind = 2
  Integer, Parameter :: quakind = 1
  Integer, Parameter :: agekind = 1
  Integer, Parameter :: realkind    = 4


  ! lower limit for allowed values of variances
  Real, Parameter :: epsilon_var  = 1.E-6


 ! ! input: land/water mask values
 ! Integer, Parameter :: MLW_SPACE    = B'00000010'
 ! Integer, Parameter :: MLW_OCEAN    = B'00000000'
 Integer(quakind), Parameter :: MLW_WATER    = B'00000011'
 Integer(quakind), Parameter :: MLW_LAND     = B'00000001'

  ! input: "AL1-cloud mask" values
  Integer(quakind), Parameter :: MCL_NOMASK   = B'00000000'
  Integer(quakind), Parameter :: MCL_CLEAR    = B'00000100'
  Integer(quakind), Parameter :: MCL_CONTAM   = B'00001000'
  Integer(quakind), Parameter :: MCL_CLOUD    = B'00001100'
  Integer(quakind), Parameter :: MCL_SNOW     = B'00010000'
  Integer(quakind), Parameter :: MCL_SHADOW   = B'00010100'
  Integer(quakind), Parameter :: MCL_CLEAR_X  = B'00011000'
  Integer(quakind), Parameter :: MCL_SNOW_X   = B'00011100'

  ! input: atmospheric correction processing flag
  Integer, Parameter :: BIT_PROC     = 7

  ! output: quality flag values
  Integer(quakind), Parameter :: QUA_MSG      = B'00000100'
  Integer(quakind), Parameter :: QUA_EPS      = B'00001000'
  !Integer(quakind), Parameter :: QUA_APRIORI  = B'00010000'
  Integer(quakind), Parameter :: QUA_NO_INPUT = B'00010000'
  Integer(quakind), Parameter :: QUA_SNOW     = B'00100000'
  Integer(quakind), Parameter :: QUA_MAJORITY = B'01000000'

! These bit flags correspond to : AL1 cloud mask values 
! starting at 0 
! Does not concern the qf of the BRDF or albedo....
  Integer, Parameter :: BIT_MSG      = 2
  Integer, Parameter :: BIT_NO_INPUT = 4
  Integer, Parameter :: BIT_SNOW     = 5
  Integer, Parameter :: BIT_FAILS    = 7
  Integer, Parameter :: BIT_EPS      = 3

  ! flag for allocate-status
  Integer :: astat

  ! flag for I/O-status
  Integer :: ios
End Module algoconf
