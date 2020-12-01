Recursive Subroutine ludcmp(a,indx,d)
  Use nrtype; USE nrutil, ONLY : assert_eq,imaxloc,nrerror,outerprod,swap
  Implicit None
  Real(SP), Dimension(:,:), Intent(INOUT) :: a
  Integer(I4B), Dimension(:), Intent(OUT) :: indx
  Real(SP), Intent(OUT) :: d
  Real(SP), Dimension(size(a,1)) :: vv 
  Real(SP), Parameter :: TINY=1.0e-20_sp
  Integer(I4B) :: j,n,imax

  n=assert_eq(size(a,1),size(a,2),size(indx),'ludcmp')
  d=1.0
  vv=maxval(abs(a),dim=2)
  If (any(vv == 0.0)) Then
     Print*, 'Warning: singular matrix in ludcmp'
  End If
  vv=1.0_sp/vv
  Do j=1,n
     imax=(j-1)+imaxloc(vv(j:n)*abs(a(j:n,j)))
     If (j /= imax) Then
        Call swap(a(imax,:),a(j,:))
        d=-d
        vv(imax)=vv(j)
     End If
     indx(j)=imax
     If (a(j,j) == 0.0) a(j,j)=TINY
     a(j+1:n,j)=a(j+1:n,j)/a(j,j)
     a(j+1:n,j+1:n)=a(j+1:n,j+1:n)-outerprod(a(j+1:n,j),a(j,j+1:n))
  End Do

End Subroutine ludcmp
