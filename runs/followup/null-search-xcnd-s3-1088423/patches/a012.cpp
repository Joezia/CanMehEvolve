void Encode::Write( const std::vector<Mesg>& mesgs )
{
    for ( std::vector<Mesg>::size_type i = 0; i < mesgs.size(); i++ )
        Write( mesgs[i] );
// noop-3-12
}
