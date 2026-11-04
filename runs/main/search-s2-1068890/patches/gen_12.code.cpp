
FIT_UINT16 Mesg::GetNum() const
{
    return (profile == FIT_NULL) ? FIT_MESG_NUM_INVALID : profile->num;
}
