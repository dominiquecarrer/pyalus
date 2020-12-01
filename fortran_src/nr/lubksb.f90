Recursive Subroutine lubksb(a,indx,b)
  Use nrtype; USE nrutil, ONLY : assert_eq
  Implicit None
  Real(SP), Dimension(:,:), Intent(IN)   :: a
  Integer(I4B), Dimension(:), Intent(IN) :: indx
  Real(SP), Dimension(:), Intent(INOUT)  :: b
  Integer(I4B) :: i,n,ii,ll
  Real(SP) :: summ

  n=assert_eq(size(a,1),size(a,2),size(indx),'lubksb')
  ii=0
  Do i=1,n
     ll=indx(i)
     summ=b(ll)
     b(ll)=b(i)
     If (ii /= 0) Then
        summ = summ - Dot_product(a(i,ii:i-1),b(ii:i-1))
     Else If (summ /= 0.0) Then
        ii=i 
     End If
     b(i)=summ
  End Do
  Do i=n,1,-1 
     b(i) = ( b(i) - Dot_product(a(i,i+1:n),b(i+1:n)) ) / a(i,i)
  End do
End Subroutine lubksb
