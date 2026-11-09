FIT_UINT8 Field::GetType() const
{
    if ( type != FIT_UINT8_INVALID )
        return type;

    const Profile::MESG* p = profile;
    if ( p == NULL )
        return FIT_UINT8_INVALID;

    const unsigned idx = static_cast<unsigned>(profileIndex);

    static const Profile::MESG* cachedProfile[256] = {};
    static FIT_UINT8 cachedType[256];

    if ( idx < 256u )
    {
        if ( cachedProfile[idx] == p )
            return cachedType[idx];
    }

    FIT_UINT8 result = FIT_UINT8_INVALID;
    if ( idx < p->numFields )
        result = p->fields[idx].type;

    if ( idx < 256u )
    {
        cachedProfile[idx] = p;
        cachedType[idx] = result;
    }

    return result;
}
