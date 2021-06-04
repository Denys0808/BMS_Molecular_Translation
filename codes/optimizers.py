####### OPTIMIZERS

def get_optimizer(CFG, model, eta):
                   
    # scale learning rates
    if CFG['device'] == 'TPU':
        eta     = eta            * xm.xrt_world_size()
        eta_min = CFG['eta_min'] * xm.xrt_world_size()
    else:
        eta_min = CFG['eta_min']

    # optimizer
    if CFG['optim'] == 'Adam':
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), 
                               lr           = eta, 
                               weight_decay = CFG['decay'])
    elif CFG['optim'] == 'AdamW':
        optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), 
                                lr           = eta, 
                                weight_decay = CFG['decay'])
    elif CFG['optim'] == 'AdamP':
        optimizer = AdamP(filter(lambda p: p.requires_grad, model.parameters()), 
                          lr           = eta, 
                          weight_decay = CFG['decay'])
    elif CFG['optim'] == 'madgrad':
        optimizer = MADGRAD(filter(lambda p: p.requires_grad, model.parameters()), 
                            lr           = eta, 
                            weight_decay = CFG['decay']) 


    return optimizer



####### SCHEDULERS

def get_scheduler(CFG, optimizer):
    
    # scale learning rates
    if CFG['device'] == 'TPU':
        eta_min = CFG['eta_min'] * xm.xrt_world_size()
    else:
        eta_min = CFG['eta_min']
    
    # scheduler after warmup
    if CFG['schedule'] == 'CosineAnnealing':
        after_scheduler = CosineAnnealingWarmRestarts(optimizer = optimizer,
                                                      T_0       = CFG['num_epochs'] - CFG['warmup'] if CFG['num_epochs'] > 1 else 1,
                                                      eta_min   = eta_min)
        
    # warmup
    scheduler = GradualWarmupScheduler(optimizer       = optimizer, 
                                       multiplier      = 1, 
                                       total_epoch     = CFG['warmup'] + 1, 
                                       after_scheduler = after_scheduler)

    return scheduler