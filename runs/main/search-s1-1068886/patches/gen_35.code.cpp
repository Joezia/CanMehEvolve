
Mesg::Mesg(const Mesg &mesg)
    : profile(mesg.profile)
    , localNum(mesg.localNum)
    , fields(std::move(mesg.fields))
    , devFields(std::move(mesg.devFields))
{
}
