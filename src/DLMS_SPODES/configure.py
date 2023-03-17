from .types import cst
from .cosem_interface_classes import cosem_interface_class as ic, collection
from . import ITE_exceptions as exc


def get_attr_index(obj: ic.COSEMInterfaceClasses) -> list[int]:
    """ return attribute indexes for reading keep configuration """
    match obj.CLASS_ID, obj.logical_name:
        case collection.Data.CLASS_ID, _:                                                        return [2]
        case collection.Register.CLASS_ID, _:                                                    return [2, 3]
        case collection.ExtendedRegister.CLASS_ID, _:                                            return [3]
        case collection.ProfileGenericVer1.CLASS_ID, cst.LogicalName(1, _, 94, 7, e) if obj.logical_name.a == 1 and obj.logical_name.c == 9 and obj.logical_name.d == 7 and 1 <= e <= 4:
            return [6, 3, 2, 4, 5, 8]
        case collection.ProfileGenericVer1.CLASS_ID, _:                                              return [6, 3, 4, 5, 8]
        case collection.Clock.CLASS_ID, _:                                                       return [8, 9]
        case collection.ScriptTable.CLASS_ID, _:                                                 return [2]
        case collection.Schedule.CLASS_ID, _:                                                    return [2]
        case collection.SpecialDaysTable.CLASS_ID, _:                                            return []
        case collection.ActivityCalendar.CLASS_ID, _:                                            return []
        case collection.SingleActionSchedule.CLASS_ID, _:                                        return [2, 3, 4]
        case collection.AssociationLNVer0.CLASS_ID, if obj.logical_name.a == 0 and obj.logical_name.c == 40 and obj.logical_name.d == 0 and obj.logical_name.e == 0:
            return []
        case collection.AssociationLNVer0.CLASS_ID, _:                                           return [4, 5, 7]
        case collection.IECHDLCSetupVer1.CLASS_ID, _:                                                return [2, 3, 4, 5, 6, 7]
        case collection.DisconnectControl.CLASS_ID, _:                                           return [3, 4]
        case collection.Limiter.CLASS_ID, _:                                                     return [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        case collection.PSTNModemConfiguration.CLASS_ID, _:                                      return [2]
        case collection.ImageTransfer.CLASS_ID, _:                                               return [2]
        case collection.GPRSModemSetup.CLASS_ID, _:                                              return [2]
        case collection.GSMDiagnosticVer0.CLASS_ID, _:                                               return []
        case collection.ClientSetup.CLASS_ID, _:                                                 return []  # not need only for client
        case collection.TCPUDPSetup.CLASS_ID, _:                                                 return [2, 3, 4, 5, 6]
        case collection.IPv4Setup.CLASS_ID, _:                                                   return []
        case collection.Arbitrator.CLASS_ID, _:                                                  return [2]
        case collection.SecuritySetupVer0.CLASS_ID, _:                                           return [2, 3, 5]
        case collection.RegisterMonitor.CLASS_ID, _:                                             return [3, 2, 4]
        case _: raise exc.NoObject(F"Configuring. Not found {obj} with {obj.CLASS_ID} for read attributes")


def get_saved_parameters(obj: ic.COSEMInterfaceClasses) -> dict[int, int]:
    """ return attribute indexes for saved keep configuration dictionary(attr_index: 0-for value 1-for type, ...)"""
    ln = obj.logical_name
    match obj.CLASS_ID, obj.logical_name:
        case collection.Data.CLASS_ID, cst.LogicalName(0, 0, 96, 1, 1) | cst.LogicalName(0, 0, 96, 1, 3) | cst.LogicalName(0, 0, 96, 1, 6) \
                                             | cst.LogicalName(0, 0, 96, 1, 8) | cst.LogicalName(1, 0, 0, 8, 4):
            return {2: 0}
        case collection.Data.CLASS_ID, _:                                                        return {2: 1}
        case collection.Register.CLASS_ID, cst.LogicalName(1, 0, 0, 6, 0) | cst.LogicalName(1, 0, 0, 6, 1) | cst.LogicalName(1, 0, 0, 6, 2) | cst.LogicalName(1, 0, 0, 6, 3) \
                                                | cst.LogicalName(1, 0, 0, 6, 4):
            return {2: 1, 3: 1}
        case collection.Register.CLASS_ID, _:                                                    return {2: 1, 3: 0}
        case collection.ExtendedRegister.CLASS_ID, _:                                            return {2: 1, 3: 0}
        case collection.ProfileGenericVer1.CLASS_ID, cst.LogicalName(1, _, 94, 7, e) if 1 <= e <= 4: return {6: 0, 3: 0, 2: 0, 4: 0, 5: 0, 8: 0}
        case collection.ProfileGenericVer1.CLASS_ID, _:                                              return {6: 0, 3: 0, 4: 0, 5: 0, 8: 0}
        case collection.Clock.CLASS_ID, _:                                                       return {8: 0, 9: 0}
        case collection.ScriptTable.CLASS_ID, _:                                                 return {2: 0}
        case collection.Schedule.CLASS_ID, _:                                                    return {2: 0}
        case collection.SpecialDaysTable.CLASS_ID, _:                                            return dict()
        case collection.ActivityCalendar.CLASS_ID, _:                                            return dict()
        case collection.SingleActionSchedule.CLASS_ID, _:                                        return {2: 0, 3: 0, 4: 0}
        case collection.AssociationLNVer0.CLASS_ID, cst.LogicalName(0, 0, 40, 0, 0):             return {3: 0}
        case collection.AssociationLNVer0.CLASS_ID, cst.LogicalName(0, 0, 40, 0, 1):             return {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 9: 0}
        case collection.AssociationLNVer0.CLASS_ID, _:                                           return {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 9: 0}
        case collection.IECHDLCSetupVer1.CLASS_ID, _:                                                return {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        case collection.DisconnectControl.CLASS_ID, _:                                           return {3: 0, 4: 0}
        case collection.Limiter.CLASS_ID, _:                                                     return {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}
        case collection.PSTNModemConfiguration.CLASS_ID, _:                                      return {2: 0}
        case collection.ImageTransfer.CLASS_ID, _:                                               return {2: 0}
        case collection.GPRSModemSetup.CLASS_ID, _:                                              return {2: 0}
        case collection.GSMDiagnosticVer0.CLASS_ID, _:                                               return dict()
        case collection.ClientSetup.CLASS_ID, _:                                                 return dict()  # not need only for client
        case collection.TCPUDPSetup.CLASS_ID, _:                                                 return {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        case collection.IPv4Setup.CLASS_ID, _:                                                   return dict()
        case collection.Arbitrator.CLASS_ID, _:                                                  return {2: 0}
        case collection.SecuritySetupVer0.CLASS_ID, _:                                           return {2: 0, 3: 0, 5: 0}
        case collection.RegisterMonitor.CLASS_ID, _:                                             return {3: 0, 2: 0, 4: 0}
        case _: raise exc.NoObject(F'Save configure. Not found {obj} with {obj.CLASS_ID} for read attributes')


if __name__ == '__main__':
    a = collection.AssociationLNVer0('0.0.1.0.0.255')
    print(a)
    b = get_attr_index(a)
    print(b)