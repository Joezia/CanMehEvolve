FIT_UINT16 Mesg::GetNum() const
{
    return (__builtin_expect(profile != FIT_NULL, 1))
        ? profile->num
        : FIT_MESG_NUM_INVALID;
}
