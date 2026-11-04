Mesg::Mesg(const Mesg &mesg)
    : profile(mesg.profile)
    , localNum(mesg.localNum)
    , fields(std::move(const_cast<Mesg&>(mesg).fields))
    , devFields(std::move(const_cast<Mesg&>(mesg).devFields))
{
}
