void Mesg::SetLocalNum(const FIT_UINT8 newLocalNum)
{
    if (newLocalNum < FIT_MAX_LOCAL_MESGS)
        localNum = newLocalNum;
// noop-2-25
}
